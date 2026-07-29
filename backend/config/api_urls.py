from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.axes.views import ResearchAxisViewSet
from apps.common.search import GlobalSearchAPIView
from apps.core.views import HomeAPIView, SiteSettingsViewSet
from apps.institutional.views import InstitutionalUnitViewSet
from apps.learning.views import CourseViewSet
from apps.metrics.views import ImpactMetricViewSet
from apps.news.views import PostViewSet
from apps.partnerships.views import ContactMessageViewSet, PartnerViewSet
from apps.people.views import PersonViewSet
from apps.portfolio.views import ProjectCategoryViewSet, ProjectViewSet
from apps.research.views import AcademicWorkViewSet, ResearchProjectViewSet
from apps.scientific.views import ScientificOutputViewSet
from apps.transparency.views import TransparencyDocumentViewSet


router = DefaultRouter()
router.register("site/settings", SiteSettingsViewSet, basename="site-settings")
router.register("institutional-units", InstitutionalUnitViewSet, basename="institutional-units")
router.register("people", PersonViewSet, basename="people")
router.register("axes", ResearchAxisViewSet, basename="axes")
router.register("projects/categories", ProjectCategoryViewSet, basename="project-categories")
router.register("projects", ProjectViewSet, basename="projects")
router.register("research-projects", ResearchProjectViewSet, basename="research-projects")
router.register("academic-works", AcademicWorkViewSet, basename="academic-works")
router.register("scientific-outputs", ScientificOutputViewSet, basename="scientific-outputs")
router.register("posts", PostViewSet, basename="posts")
router.register("courses", CourseViewSet, basename="courses")
router.register("transparency-documents", TransparencyDocumentViewSet, basename="transparency-documents")
router.register("partners", PartnerViewSet, basename="partners")
router.register("metrics/impact", ImpactMetricViewSet, basename="impact-metrics")
router.register("contact", ContactMessageViewSet, basename="contact")

urlpatterns = [
    path("site/home/", HomeAPIView.as_view(), name="site-home"),
    path("search/", GlobalSearchAPIView.as_view(), name="global-search"),
    path("", include(router.urls)),
]
