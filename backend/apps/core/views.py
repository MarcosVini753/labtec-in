from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import EditorialStatus
from apps.common.viewsets import PublicReadOnlyModelViewSet
from apps.core.models import HeroBanner, InstitutionalSection, SiteSettings, SocialLink
from apps.core.serializers import (
    HeroBannerSerializer,
    InstitutionalSectionSerializer,
    SiteSettingsSerializer,
    SocialLinkSerializer,
)
from apps.metrics.models import ImpactMetric
from apps.metrics.serializers import ImpactMetricSerializer
from apps.news.models import Post
from apps.news.serializers import PostSerializer
from apps.people.models import Person
from apps.people.serializers import PersonSummarySerializer
from apps.portfolio.models import Project
from apps.portfolio.serializers import ProjectSerializer


class SiteSettingsViewSet(PublicReadOnlyModelViewSet):
    lookup_field = "pk"
    queryset = SiteSettings.objects.select_related("unit").order_by("pk")
    serializer_class = SiteSettingsSerializer


class HomeAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        unit_slug = "labtec-in"
        settings = (
            SiteSettings.objects.select_related("unit")
            .filter(is_active=True, unit__slug=unit_slug)
            .first()
        )
        heroes = (
            HeroBanner.objects.select_related("unit")
            .filter(is_published=True, unit__slug=unit_slug)
            .order_by("display_order", "title")
        )
        sections = (
            InstitutionalSection.objects.select_related("unit")
            .filter(is_published=True, unit__slug=unit_slug)
            .order_by("display_order", "title")
        )
        social_links = (
            SocialLink.objects.select_related("unit")
            .filter(is_active=True, unit__slug=unit_slug)
            .order_by("display_order", "label")
        )

        latest_posts = (
            Post.objects.filter(editorial_status=EditorialStatus.PUBLISHED, unit__slug=unit_slug)
            .order_by("-published_at", "-created_at")[:6]
        )
        featured_projects = (
            Project.objects.filter(editorial_status=EditorialStatus.PUBLISHED, unit__slug=unit_slug)
            .order_by("-published_at", "-created_at")[:6]
        )
        impact_metrics = (
            ImpactMetric.objects.filter(is_active=True, unit__slug=unit_slug)
            .order_by("display_order", "label")
        )
        people = (
            Person.objects.filter(is_active=True)
            .prefetch_related("institution_memberships__unit")
            .order_by("display_order", "full_name")
        )

        return Response(
            {
                "settings": SiteSettingsSerializer(settings, context={"request": request}).data if settings else None,
                "heroes": HeroBannerSerializer(heroes, many=True, context={"request": request}).data,
                "sections": InstitutionalSectionSerializer(sections, many=True, context={"request": request}).data,
                "social_links": SocialLinkSerializer(social_links, many=True, context={"request": request}).data,
                "posts": PostSerializer(latest_posts, many=True, context={"request": request}).data,
                "projects": ProjectSerializer(featured_projects, many=True, context={"request": request}).data,
                "impact_metrics": ImpactMetricSerializer(impact_metrics, many=True, context={"request": request}).data,
                "people": PersonSummarySerializer(people, many=True, context={"request": request}).data,
            }
        )
