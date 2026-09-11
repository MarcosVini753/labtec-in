from django.contrib import admin
from django.core.exceptions import PermissionDenied

from apps.accounts.models import Profile
from apps.common.admin_scoping import (
    UnitScopedAdminMixin,
    can_publish,
    get_admin_profile,
    has_active_admin_scope,
    is_global_admin,
    is_lab_coordinator,
)
from apps.partnerships.models import ContactMessage, Partner


@admin.register(Partner)
class PartnerAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = "units"
    unit_lookup_is_many = True
    shared_units_lookup = "units"
    list_display = ("name", "unit_list", "partner_type", "is_active", "display_order")
    list_filter = ("units", "partner_type", "is_active")
    search_fields = ("name", "description", "website", "units__name", "units__acronym")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("units",)
    fieldsets = (
        ("Identificação", {"fields": ("units", "name", "slug", "partner_type")}),
        ("Conteúdo", {"fields": ("description", "logo", "website")}),
        ("Exibição", {"fields": ("is_active", "display_order")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("units")

    def _submitted_scope_is_allowed(self, request, obj):
        if is_global_admin(request):
            return True
        if obj.pk:
            return self.scope_queryset(request, obj.__class__._default_manager.filter(pk=obj.pk)).exists()
        profile = get_admin_profile(request)
        return bool(profile and profile.accessible_unit_ids())

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        unit_ids = set(form.instance.units.values_list("pk", flat=True))
        profile = get_admin_profile(request)
        if not is_global_admin(request) and (
            not profile
            or (not unit_ids and not profile.is_lab_coordinator)
            or not unit_ids.issubset(profile.accessible_unit_ids())
            or (len(unit_ids) > 1 and not can_publish(request))
        ):
            raise PermissionDenied("O parceiro compartilhado está fora do escopo institucional autorizado.")

    @admin.display(description="Unidades")
    def unit_list(self, obj):
        return ", ".join(unit.acronym or unit.name for unit in obj.units.all()) or "—"


@admin.register(ContactMessage)
class ContactMessageAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = None
    list_display = ("subject", "contact_type", "name", "email", "organization", "status", "created_at", "responded_at")
    list_filter = ("contact_type", "status", "created_at", "responded_at")
    search_fields = ("subject", "name", "email", "organization", "message")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Mensagem", {"fields": ("contact_type", "subject", "message", "status")}),
        ("Contato", {"fields": ("name", "email", "organization")}),
        ("Atendimento", {"fields": ("responded_at",)}),
        ("Auditoria", {"fields": ("created_at", "updated_at")}),
    )

    def has_module_permission(self, request):
        if is_global_admin(request):
            return True
        profile = get_admin_profile(request)
        return bool(
            has_active_admin_scope(request)
            and profile
            and profile.role
            in {Profile.AdminRole.LAB_COORDINATOR, Profile.AdminRole.UNIT_COORDINATOR}
        )

    def get_queryset(self, request):
        queryset = admin.ModelAdmin.get_queryset(self, request)
        return queryset if self.has_module_permission(request) else queryset.none()

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return (is_global_admin(request) or is_lab_coordinator(request)) and super().has_add_permission(request)

    def get_readonly_fields(self, request, obj=None):
        readonly = set(super().get_readonly_fields(request, obj))
        profile = get_admin_profile(request)
        if profile and profile.role == Profile.AdminRole.UNIT_COORDINATOR:
            readonly.update(("contact_type", "subject", "message", "name", "email", "organization"))
        return tuple(readonly)

    def _submitted_scope_is_allowed(self, request, obj):
        return self.has_module_permission(request)
