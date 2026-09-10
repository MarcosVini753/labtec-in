from django.db import models

from apps.common.models import BaseModel, EditorialStatus


class Post(BaseModel):
    unit = models.ForeignKey(
        "institutional.InstitutionalUnit",
        on_delete=models.PROTECT,
        related_name="posts",
    )
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    axis = models.ForeignKey("axes.ResearchAxis", on_delete=models.SET_NULL, related_name="posts", blank=True, null=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="news/posts/", blank=True)
    body_image = models.ImageField(upload_to="news/posts/", blank=True)
    editorial_status = models.CharField(max_length=32, choices=EditorialStatus.choices, default=EditorialStatus.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    include_in_parent_ecosystem = models.BooleanField(
        default=False,
        help_text="Inclui este conteúdo no recorte público da unidade mãe.",
    )

    class Meta:
        ordering = ("-published_at", "title")
        verbose_name = "post"
        verbose_name_plural = "posts"

    def __str__(self) -> str:
        return self.title


class PostLink(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=240)
    url = models.URLField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "id")
        constraints = [
            models.UniqueConstraint(fields=("post", "url"), name="unique_post_link_url"),
        ]

    def __str__(self) -> str:
        return self.label
