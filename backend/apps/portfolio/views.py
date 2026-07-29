from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from apps.common.viewsets import ECOSYSTEM_UNIT_PARAMETER, PublicReadOnlyModelViewSet
from apps.portfolio.models import Project, ProjectCategory
from apps.portfolio.serializers import ProjectCategorySerializer, ProjectSerializer


class ProjectCategoryViewSet(PublicReadOnlyModelViewSet):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    search_fields = ("name", "description")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            ECOSYSTEM_UNIT_PARAMETER,
            OpenApiParameter("axis", OpenApiTypes.STR, description="Slug do eixo de pesquisa."),
            OpenApiParameter("category", OpenApiTypes.STR, description="Slug da categoria de portfólio."),
            OpenApiParameter("status", OpenApiTypes.STR, description="Slug do status de execução."),
            OpenApiParameter("year", OpenApiTypes.INT, description="Ano do projeto."),
            OpenApiParameter("search", OpenApiTypes.STR, description="Busca textual."),
        ],
    ),
)
class ProjectViewSet(PublicReadOnlyModelViewSet):
    queryset = Project.objects.select_related("unit", "axis__unit", "category", "status").prefetch_related(
        "axis__mentorships__person",
        "team_members__person",
        "results",
        "links",
        "startup_profile",
    )
    serializer_class = ProjectSerializer
    search_fields = ("title", "summary", "area", "problem", "solution")
