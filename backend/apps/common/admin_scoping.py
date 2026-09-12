from __future__ import annotations

from django.apps import apps
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.db.models import Q, QuerySet

from apps.accounts.models import Profile
from apps.common.models import EditorialStatus


def get_admin_profile(request):
    if not request.user.is_authenticated or request.user.is_superuser:
        return None
    try:
        return request.user.profile
    except Profile.DoesNotExist:
        return None


def has_active_admin_scope(request) -> bool:
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        return False
    if request.user.is_superuser:
        return True
    profile = get_admin_profile(request)
    if not profile or not profile.is_active_admin or profile.role not in Profile.AdminRole.values:
        return False
    if profile.role == Profile.AdminRole.MENTOR and not profile.person_id:
        return False
    return bool(profile.accessible_unit_ids())


def is_global_admin(request) -> bool:
    return bool(
        request.user.is_authenticated
        and request.user.is_active
        and request.user.is_staff
        and request.user.is_superuser
    )


def is_lab_coordinator(request) -> bool:
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        return False
    profile = get_admin_profile(request)
    return bool(profile and profile.is_lab_coordinator)


def can_publish(request) -> bool:
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        return False
    if request.user.is_superuser:
        return True
    profile = get_admin_profile(request)
    return bool(profile and profile.can_publish)


def can_edit_drafts(request) -> bool:
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        return False
    if request.user.is_superuser:
        return True
    profile = get_admin_profile(request)
    return bool(
        profile
        and profile.is_active_admin
        and (profile.role != Profile.AdminRole.LAB_COORDINATOR or profile.is_lab_coordinator)
        and profile.role
        in {
            Profile.AdminRole.LAB_COORDINATOR,
            Profile.AdminRole.UNIT_COORDINATOR,
            Profile.AdminRole.MENTOR,
        }
    )


def _has_model_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
    except Exception:  # FieldDoesNotExist without importing another symbol.
        return False
    return True


def _published_filter(model) -> Q:
    published = Q()
    if _has_model_field(model, "editorial_status"):
        published |= Q(editorial_status__in=(EditorialStatus.PUBLISHED, EditorialStatus.ARCHIVED))
    if not published:
        for field_name in _publication_boolean_fields(model):
            published |= Q(**{field_name: True})
    return published


def _publication_boolean_fields(model) -> tuple[str, ...]:
    if _has_model_field(model, "editorial_status"):
        return ()
    if _has_model_field(model, "is_published"):
        return ("is_published",)
    return tuple(field_name for field_name in ("is_active", "is_public") if _has_model_field(model, field_name))


def _related_queryset_for_request(queryset: QuerySet, request) -> QuerySet:
    """Limit autocomplete and form choices to the request's institutional scope."""
    if is_global_admin(request):
        return queryset

    profile = get_admin_profile(request)
    if not profile or not profile.is_active_admin:
        return queryset.none()

    unit_ids = profile.accessible_unit_ids()
    model = queryset.model
    if model._meta.label_lower == "institutional.institutionalunit":
        return queryset.filter(pk__in=unit_ids)
    if model._meta.label_lower == "axes.researchaxis":
        scoped = queryset.filter(unit_id__in=unit_ids)
        if profile.role == Profile.AdminRole.MENTOR:
            scoped = scoped.filter(pk__in=profile.mentor_axis_ids())
        return scoped
    if model._meta.label_lower == "people.person":
        scope = Q(institution_memberships__unit_id__in=unit_ids)
        if profile.is_lab_coordinator:
            scope |= Q(institution_memberships__isnull=True)
        return queryset.filter(scope).distinct()
    if _has_model_field(model, "unit"):
        scoped = queryset.filter(unit_id__in=unit_ids)
        if profile.role == Profile.AdminRole.MENTOR:
            if _has_model_field(model, "axis"):
                scoped = scoped.filter(axis_id__in=profile.mentor_axis_ids())
            elif model._meta.label_lower == "research.academicwork":
                scoped = scoped.filter(research_project__axis_id__in=profile.mentor_axis_ids())
        return scoped
    if _has_model_field(model, "units"):
        scope = Q(units__id__in=unit_ids)
        if profile.is_lab_coordinator:
            scope |= Q(units__isnull=True)
        return queryset.filter(scope).distinct()
    return queryset


class UnitScopedAdminMixin:
    """Django Admin policy for records scoped by unit and, for mentors, axis."""

    unit_lookup: str | None = "unit"
    axis_lookup: str | None = None
    unit_lookup_is_many = False
    access_level = "scoped"  # scoped, lab, admin
    lab_only = False
    shared_units_lookup: str | None = None
    publication_lookup: str | None = None
    mentor_requires_axis = True

    def get_queryset(self, request):
        return self.scope_queryset(request, super().get_queryset(request))

    def scope_queryset(self, request, queryset):
        if is_global_admin(request):
            return queryset
        profile = get_admin_profile(request)
        if (
            not profile
            or not profile.is_active_admin
            or (profile.role == Profile.AdminRole.LAB_COORDINATOR and not profile.is_lab_coordinator)
        ):
            return queryset.none()
        if self.access_level == "admin":
            return queryset.none()
        if self.access_level == "lab":
            return queryset if profile.is_lab_coordinator else queryset.none()
        if profile.is_lab_coordinator:
            if not self.unit_lookup:
                return queryset
            scope = Q(**{f"{self.unit_lookup}__in": profile.accessible_unit_ids()})
            if self.unit_lookup_is_many:
                scope |= Q(**{f"{self.unit_lookup}__isnull": True})
            scoped = queryset.filter(scope)
            return scoped.distinct() if self.unit_lookup_is_many else scoped

        if profile.role == Profile.AdminRole.MENTOR and self.mentor_requires_axis and not self.axis_lookup:
            return queryset.none()
        if not self.unit_lookup:
            return queryset.none()

        unit_ids = profile.accessible_unit_ids()
        scoped = queryset.filter(**{f"{self.unit_lookup}__in": unit_ids})
        if profile.role == Profile.AdminRole.MENTOR and self.mentor_requires_axis:
            scoped = scoped.filter(**{f"{self.axis_lookup}__in": profile.mentor_axis_ids()})
        return scoped.distinct() if self.unit_lookup_is_many else scoped

    def has_module_permission(self, request):
        if not has_active_admin_scope(request):
            return False
        if self.access_level == "admin":
            return is_global_admin(request)
        if self.access_level == "lab":
            return is_global_admin(request) or is_lab_coordinator(request)
        if self.lab_only:
            return is_global_admin(request) or is_lab_coordinator(request)
        return True

    def has_view_permission(self, request, obj=None):
        if not self.has_module_permission(request):
            return False
        if obj is None or is_global_admin(request):
            return True
        return self.scope_queryset(request, obj.__class__._default_manager.filter(pk=obj.pk)).exists()

    def has_add_permission(self, request):
        if not self.has_module_permission(request) or not can_edit_drafts(request):
            return False
        profile = get_admin_profile(request)
        if (
            profile
            and profile.role == Profile.AdminRole.MENTOR
            and self.mentor_requires_axis
            and (not self.axis_lookup or not profile.mentor_axis_ids())
        ):
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not self.has_module_permission(request) or not can_edit_drafts(request):
            return False
        if obj is None:
            return True
        if not self.has_view_permission(request, obj):
            return False
        publication_object = self._resolve_lookup_value(obj, self.publication_lookup) if self.publication_lookup else obj
        if self._is_published(publication_object) and not can_publish(request):
            return False
        if self.shared_units_lookup and not can_publish(request):
            units = getattr(obj, self.shared_units_lookup).all()
            if units.count() > 1:
                return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request) and can_publish(request) and (
            obj is None or self.has_view_permission(request, obj)
        )

    def can_publish(self, request):
        return can_publish(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not can_publish(request):
            actions.pop("mark_as_published", None)
            actions.pop("mark_as_archived", None)
        return actions

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        if not can_publish(request) and self._is_publication_parent_autocomplete(request):
            published = _published_filter(self.model)
            if published:
                queryset = queryset.exclude(published)
        return queryset, may_have_duplicates

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not can_publish(request):
            for field_name in ("published_at",):
                if _has_model_field(self.model, field_name) and field_name not in readonly:
                    readonly.append(field_name)
            if not self.publication_lookup:
                for field_name in _publication_boolean_fields(self.model):
                    if field_name not in readonly:
                        readonly.append(field_name)
        return tuple(readonly)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if not can_publish(request) and self._is_editorial_status_field(db_field):
            kwargs["choices"] = [
                (EditorialStatus.DRAFT, EditorialStatus.DRAFT.label),
                (EditorialStatus.IN_REVIEW, EditorialStatus.IN_REVIEW.label),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if formfield and formfield.queryset is not None:
            formfield.queryset = _related_queryset_for_request(formfield.queryset, request)
            publication_field = (self.publication_lookup or "").split("__", 1)[0]
            if not can_publish(request) and db_field.name == publication_field:
                published = _published_filter(formfield.queryset.model)
                if published:
                    formfield.queryset = formfield.queryset.exclude(published)
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if formfield and formfield.queryset is not None:
            formfield.queryset = _related_queryset_for_request(formfield.queryset, request)
        return formfield

    def save_model(self, request, obj, form, change):
        allowed = self.has_change_permission(request, obj) if change else self.has_add_permission(request)
        if not allowed or not self._submitted_scope_is_allowed(request, obj):
            raise PermissionDenied("O objeto está fora do escopo institucional autorizado.")
        if not can_publish(request) and not self.publication_lookup:
            for field_name in _publication_boolean_fields(type(obj)):
                setattr(obj, field_name, False)
        publication_object = self._resolve_lookup_value(obj, self.publication_lookup) if self.publication_lookup else obj
        if not can_publish(request) and self._is_published(publication_object):
            raise PermissionDenied("Registros publicados só podem ser alterados pela coordenação do LABTEC.IN.")
        if not can_publish(request) and self._is_submitted_as_final(obj):
            raise PermissionDenied("Somente superusuários e a coordenação do LABTEC.IN podem publicar ou arquivar.")
        return super().save_model(request, obj, form, change)

    @staticmethod
    def _is_editorial_status_field(field) -> bool:
        return field.name == "editorial_status"

    @classmethod
    def _is_published(cls, obj) -> bool:
        if getattr(obj, "editorial_status", None) in {
            EditorialStatus.PUBLISHED,
            EditorialStatus.ARCHIVED,
        }:
            return True
        return any(getattr(obj, field_name, False) for field_name in _publication_boolean_fields(type(obj)))

    @classmethod
    def _is_submitted_as_final(cls, obj) -> bool:
        return getattr(obj, "editorial_status", None) in {
            EditorialStatus.PUBLISHED,
            EditorialStatus.ARCHIVED,
        }

    def _submitted_scope_is_allowed(self, request, obj) -> bool:
        if is_global_admin(request):
            return True
        profile = get_admin_profile(request)
        if not profile:
            return False
        if self.access_level == "lab":
            return profile.is_lab_coordinator
        if self.access_level != "scoped":
            return False
        if self.unit_lookup_is_many:
            if not obj.pk:
                return profile.is_lab_coordinator
            return self.scope_queryset(request, obj.__class__._default_manager.filter(pk=obj.pk)).exists()

        unit = self._resolve_lookup_value(obj, self.unit_lookup)
        unit_id = getattr(unit, "pk", unit)
        if profile.is_lab_coordinator:
            return unit_id in profile.accessible_unit_ids()
        if not unit_id or unit_id not in profile.accessible_unit_ids():
            return False
        if profile.role == Profile.AdminRole.MENTOR and self.mentor_requires_axis:
            axis = self._resolve_lookup_value(obj, self.axis_lookup)
            axis_id = getattr(axis, "pk", axis)
            return bool(axis_id and axis_id in profile.mentor_axis_ids())
        return True

    def _is_publication_parent_autocomplete(self, request) -> bool:
        app_label = request.GET.get("app_label")
        model_name = request.GET.get("model_name")
        field_name = request.GET.get("field_name")
        if not all((app_label, model_name, field_name)):
            return False
        try:
            source_model = apps.get_model(app_label, model_name)
            source_admin = self.admin_site._registry[source_model]
            source_field = source_model._meta.get_field(field_name)
        except (FieldDoesNotExist, LookupError, KeyError):
            return False
        publication_field = (getattr(source_admin, "publication_lookup", None) or "").split(
            "__", 1
        )[0]
        return (
            publication_field == source_field.name
            and source_field.remote_field is not None
            and source_field.remote_field.model is self.model
        )

    @staticmethod
    def _resolve_lookup_value(obj, lookup):
        value = obj
        for part in (lookup or "").split("__"):
            if not part:
                return None
            value = getattr(value, part, None)
            if value is None:
                return None
        return value


class AdminOnlyAdminMixin(UnitScopedAdminMixin):
    access_level = "admin"
    unit_lookup = None


class LabCoordinatorOnlyAdminMixin(UnitScopedAdminMixin):
    access_level = "lab"
    unit_lookup = None


class ReferenceAdminMixin(UnitScopedAdminMixin):
    """Expose scoped autocomplete/search while reserving catalogue management."""

    management_access = "admin"  # admin, lab, scoped
    mentor_can_manage = False
    unit_lookup = None

    def scope_queryset(self, request, queryset):
        if self.unit_lookup:
            return super().scope_queryset(request, queryset)
        return queryset if has_active_admin_scope(request) else queryset.none()

    def _can_manage(self, request) -> bool:
        if is_global_admin(request):
            return True
        if self.management_access == "lab":
            return is_lab_coordinator(request)
        if self.management_access != "scoped" or not can_edit_drafts(request):
            return False
        profile = get_admin_profile(request)
        return bool(profile and (self.mentor_can_manage or profile.role != Profile.AdminRole.MENTOR))

    def has_module_permission(self, request):
        return self._can_manage(request)

    def has_view_permission(self, request, obj=None):
        if not has_active_admin_scope(request):
            return False
        if obj is None:
            return True
        return self.scope_queryset(request, obj.__class__._default_manager.filter(pk=obj.pk)).exists()

    def has_add_permission(self, request):
        if self.unit_lookup_is_many and self.unit_lookup and not (
            is_global_admin(request) or is_lab_coordinator(request)
        ):
            return False
        return self._can_manage(request)

    def has_change_permission(self, request, obj=None):
        if not self._can_manage(request) or (obj is not None and not self.has_view_permission(request, obj)):
            return False
        return obj is None or can_publish(request) or not self._is_published(obj)

    def has_delete_permission(self, request, obj=None):
        return can_publish(request) and self.has_change_permission(request, obj)


class UnitScopedInlineMixin:
    """Apply the parent ModelAdmin policy to its inline and related choices."""

    def _parent_admin(self, obj):
        return self.admin_site._registry.get(type(obj)) if obj is not None else None

    def has_view_permission(self, request, obj=None):
        parent_admin = self._parent_admin(obj)
        return parent_admin.has_view_permission(request, obj) if parent_admin else has_active_admin_scope(request)

    def has_add_permission(self, request, obj=None):
        parent_admin = self._parent_admin(obj)
        return parent_admin.has_change_permission(request, obj) if parent_admin and obj else can_edit_drafts(request)

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_add_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if formfield and formfield.queryset is not None:
            formfield.queryset = _related_queryset_for_request(formfield.queryset, request)
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if formfield and formfield.queryset is not None:
            formfield.queryset = _related_queryset_for_request(formfield.queryset, request)
        return formfield
