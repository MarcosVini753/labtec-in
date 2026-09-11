from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from apps.accounts.models import Profile
from apps.common.admin_scoping import AdminOnlyAdminMixin


class ProfileAdminForm(forms.ModelForm):
    is_active_admin = forms.BooleanField(label="Administrador ativo", required=False, initial=False)

    class Meta:
        model = Profile
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("is_active_admin"):
            return cleaned_data

        role = cleaned_data.get("role")
        person = cleaned_data.get("person")
        primary_unit = cleaned_data.get("primary_unit")
        authorized_units = cleaned_data.get("authorized_units")
        unit_slugs = (
            set(authorized_units.values_list("slug", flat=True))
            if authorized_units is not None
            else set()
        )
        if primary_unit:
            unit_slugs.add(primary_unit.slug)

        if role == Profile.AdminRole.LAB_COORDINATOR and getattr(primary_unit, "slug", None) != "labtec-in":
            self.add_error(
                "primary_unit",
                "A coordenação do LABTEC.IN deve usar LABTEC.IN como unidade principal.",
            )
        elif role == Profile.AdminRole.UNIT_COORDINATOR and not unit_slugs:
            self.add_error("primary_unit", "Informe uma unidade principal ou ao menos uma unidade autorizada.")
        elif role == Profile.AdminRole.MENTOR:
            if "latec" not in unit_slugs:
                self.add_error("primary_unit", "O orientador deve ter a LATEC como unidade principal ou autorizada.")
            if not person:
                self.add_error("person", "Vincule o orientador a uma pessoa.")
        return cleaned_data


class RequiredStaffProfileFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not self.instance.is_staff or self.instance.is_superuser:
            return
        active_profiles = [
            form
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE") and form.cleaned_data.get("is_active_admin")
        ]
        if not active_profiles:
            raise ValidationError("Um membro da equipe deve possuir um perfil administrativo ativo e válido.")


class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileAdminForm
    formset = RequiredStaffProfileFormSet
    extra = 1
    max_num = 1
    can_delete = True
    autocomplete_fields = ("person", "primary_unit", "authorized_units")


@admin.register(Profile)
class ProfileAdmin(AdminOnlyAdminMixin, admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ("user", "person", "role", "primary_unit", "inherit_descendants", "is_active_admin", "updated_at")
    list_filter = ("role", "primary_unit", "inherit_descendants", "is_active_admin")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "person__full_name",
        "primary_unit__name",
        "primary_unit__acronym",
    )
    autocomplete_fields = ("user", "person", "primary_unit", "authorized_units")


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class ScopedUserAdmin(AdminOnlyAdminMixin, UserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        return [] if obj and obj.is_superuser else super().get_inline_instances(request, obj)


@admin.register(Group)
class ScopedGroupAdmin(AdminOnlyAdminMixin, GroupAdmin):
    pass
