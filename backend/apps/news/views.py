from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from apps.common.viewsets import ECOSYSTEM_UNIT_PARAMETER, PublicReadOnlyModelViewSet
from apps.news.models import Post
from apps.news.serializers import PostSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            ECOSYSTEM_UNIT_PARAMETER,
            OpenApiParameter("axis", OpenApiTypes.STR, description="Slug do eixo de pesquisa."),
            OpenApiParameter("year", OpenApiTypes.INT, description="Ano de publicação."),
            OpenApiParameter("search", OpenApiTypes.STR, description="Busca textual."),
        ],
    ),
)
class PostViewSet(PublicReadOnlyModelViewSet):
    queryset = Post.objects.select_related("unit", "axis__unit").prefetch_related(
        "axis__mentorships__person",
        "links",
    )
    serializer_class = PostSerializer
    search_fields = ("title", "summary", "content")
