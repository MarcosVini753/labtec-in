from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core import web_views


urlpatterns = [
    path("", web_views.home, name="home"),
    path("unidades/<slug:slug>/", web_views.unit_detail, name="unit-detail"),
    path("sobre/", web_views.about, name="about"),
    path("portfolio/", web_views.portfolio, name="portfolio"),
    path("portfolio/projetos/", web_views.projects, name="projects"),
    path("portfolio/projetos/startups/", web_views.startups, name="startups"),
    path("portfolio/projetos/<slug:slug>/", web_views.project_detail, name="project-detail"),
    path("portfolio/pesquisas/", web_views.research, name="research"),
    path("portfolio/pesquisas/<slug:slug>/", web_views.research_detail, name="research-detail"),
    path("portfolio/tccs/", web_views.academic_works, name="academic-works"),
    path("portfolio/tccs/<slug:slug>/", web_views.academic_work_detail, name="academic-work-detail"),
    path("portfolio/producao-cientifica/", web_views.scientific_outputs, name="scientific-outputs"),
    path("portfolio/producao-cientifica/<slug:slug>/", web_views.scientific_output_detail, name="scientific-output-detail"),
    path("portfolio/transparencia/", web_views.transparency, name="transparency"),
    path("portfolio/transparencia/<slug:slug>/", web_views.transparency_detail, name="transparency-detail"),
    path("noticias/", web_views.news, name="news"),
    path("noticias/<slug:slug>/", web_views.news_detail, name="news-detail"),
    path("capacitacao/", web_views.courses, name="courses"),
    path("capacitacao/<slug:slug>/", web_views.course_detail, name="course-detail"),
    path("parceiros/", web_views.partners, name="partners"),
    path("contato/", web_views.contact, name="contact"),
    path("busca/", web_views.search, name="search"),
    path("entrar/", web_views.staff_login, name="staff-login"),
    path("sair/", web_views.staff_logout, name="staff-logout"),
    path("admin/dashboard/", web_views.admin_dashboard, name="admin-dashboard"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
