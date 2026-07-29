from django.contrib import admin

from apps.common.admin_actions import EDITORIAL_ADMIN_ACTIONS
from apps.common.admin_scoping import ReferenceAdminMixin, UnitScopedAdminMixin, UnitScopedInlineMixin
from apps.portfolio.models import (
    Project,
    ProjectCategory,
    ProjectLink,
    ProjectResult,
    ProjectStartupProfile,
    ProjectStatus,
    ProjectTeamMember,
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ReferenceAdminMixin, admin.ModelAdmin):
    management_access = "lab"
    list_display = ("name", "slug", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProjectStatus)
class ProjectStatusAdmin(ReferenceAdminMixin, admin.ModelAdmin):
    management_access = "lab"
    list_display = ("name", "slug", "display_order")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProjectTeamMemberInline(UnitScopedInlineMixin, admin.TabularInline):
    model = ProjectTeamMember
    extra = 0
    autocomplete_fields = ("person",)


class ProjectResultInline(UnitScopedInlineMixin, admin.TabularInline):
    model = ProjectResult
    extra = 0


class ProjectLinkInline(UnitScopedInlineMixin, admin.TabularInline):
    model = ProjectLink
    extra = 0


class ProjectStartupProfileInline(UnitScopedInlineMixin, admin.StackedInline):
    model = ProjectStartupProfile
    extra = 0


@admin.register(Project)
class ProjectAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    axis_lookup = "axis"
    list_display = ("title", "unit", "axis", "category", "status", "editorial_status", "include_in_parent_ecosystem", "year")
    list_filter = ("unit", "axis", "category", "status", "editorial_status", "include_in_parent_ecosystem", "year")
    search_fields = ("title", "summary", "area", "problem", "solution", "unit__name", "unit__acronym")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("unit", "axis", "category", "status")
    list_select_related = ("unit", "axis", "category", "status")
    actions = EDITORIAL_ADMIN_ACTIONS
    fieldsets = (
        ("Identificação", {"fields": ("unit", "title", "slug", "axis", "category", "area", "status", "year")}),
        ("Conteúdo", {"fields": ("summary", "problem", "solution", "cover_image")}),
        ("Publicação", {"fields": ("editorial_status", "published_at", "include_in_parent_ecosystem")}),
    )
    inlines = (ProjectStartupProfileInline, ProjectTeamMemberInline, ProjectResultInline, ProjectLinkInline)


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = "project__unit"
    axis_lookup = "project__axis"
    publication_lookup = "project"
    list_display = ("project", "person", "role", "is_lead", "display_order")
    list_filter = ("is_lead", "role")
    search_fields = ("project__title", "person__full_name", "role")
    autocomplete_fields = ("project", "person")


@admin.register(ProjectResult)
class ProjectResultAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = "project__unit"
    axis_lookup = "project__axis"
    publication_lookup = "project"
    list_display = ("title", "project", "result_type", "display_order")
    list_filter = ("result_type",)
    search_fields = ("title", "description", "project__title")
    autocomplete_fields = ("project",)


@admin.register(ProjectLink)
class ProjectLinkAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = "project__unit"
    axis_lookup = "project__axis"
    publication_lookup = "project"
    list_display = ("label", "project", "link_type", "display_order")
    list_filter = ("link_type",)
    search_fields = ("label", "url", "project__title")
    autocomplete_fields = ("project",)
