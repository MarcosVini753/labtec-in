from django.contrib import admin

from apps.common.admin_actions import EDITORIAL_ADMIN_ACTIONS
from apps.common.admin_scoping import UnitScopedAdminMixin, UnitScopedInlineMixin
from apps.news.models import Post, PostLink


class PostLinkInline(UnitScopedInlineMixin, admin.TabularInline):
    model = PostLink
    extra = 0


@admin.register(Post)
class PostAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    axis_lookup = "axis"
    list_display = ("title", "unit", "axis", "editorial_status", "include_in_parent_ecosystem", "published_at")
    list_filter = ("unit", "editorial_status", "axis", "include_in_parent_ecosystem")
    search_fields = ("title", "summary", "content", "unit__name", "unit__acronym")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("unit", "axis")
    list_select_related = ("unit", "axis")
    actions = EDITORIAL_ADMIN_ACTIONS
    fieldsets = (
        ("Identificação", {"fields": ("unit", "title", "slug", "axis")}),
        ("Conteúdo", {"fields": ("summary", "content", "cover_image", "body_image")}),
        ("Publicação", {"fields": ("editorial_status", "published_at", "include_in_parent_ecosystem")}),
    )
    inlines = (PostLinkInline,)


@admin.register(PostLink)
class PostLinkAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    unit_lookup = "post__unit"
    axis_lookup = "post__axis"
    publication_lookup = "post"
    list_display = ("label", "post", "display_order")
    search_fields = ("label", "url", "post__title")
    autocomplete_fields = ("post",)
