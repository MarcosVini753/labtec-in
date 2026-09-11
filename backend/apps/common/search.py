from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import EditorialStatus
from apps.institutional.models import InstitutionMembership
from apps.learning.models import Course
from apps.news.models import Post
from apps.partnerships.models import Partner
from apps.people.models import Person
from apps.portfolio.models import Project
from apps.research.models import AcademicWork, ResearchProject
from apps.scientific.models import ScientificOutput
from apps.transparency.models import TransparencyDocument


def search_result_url(kind, slug):
    routes = {
        "person": f"/sobre/#pessoa-{slug}",
        "project": f"/portfolio/projetos/{slug}/",
        "research_project": f"/portfolio/pesquisas/{slug}/",
        "academic_work": f"/portfolio/tccs/{slug}/",
        "scientific_output": f"/portfolio/producao-cientifica/{slug}/",
        "post": f"/noticias/{slug}/",
        "course": f"/capacitacao/{slug}/",
        "transparency_document": f"/portfolio/transparencia/{slug}/",
        "partner": f"/parceiros/#{slug}",
    }
    return routes[kind]


def public_search_results(query, requested_type="", unit_slug=""):
    """Retorna apenas resultados que podem ser exibidos no portal público."""
    query = query.strip()
    requested_type = requested_type.strip()
    unit_slug = unit_slug.strip()
    if not query:
        return []

    results = []
    public_memberships = InstitutionMembership.objects.filter(
        is_active=True,
        is_public=True,
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=timezone.localdate()),
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.localdate()),
    )

    def add(kind, title, slug, summary, unit):
        if requested_type and requested_type != kind:
            return
        if unit_slug and (not unit or unit.slug != unit_slug):
            return
        results.append(
            {
                "type": kind,
                "title": title,
                "slug": slug,
                "summary": summary,
                "unit": {"name": unit.name, "slug": unit.slug} if unit else None,
                "url": search_result_url(kind, slug),
            }
        )

    for person in Person.objects.filter(
        Q(full_name__icontains=query) | Q(short_bio__icontains=query),
        is_active=True,
    ).prefetch_related("institution_memberships__unit"):
        membership = next(
            (
                item
                for item in person.institution_memberships.all()
                if item in public_memberships and (not unit_slug or item.unit.slug == unit_slug)
            ),
            None,
        )
        if membership:
            add("person", person.full_name, person.slug, person.short_bio, membership.unit)

    content_models = (
        ("project", Project, ("title", "summary")),
        ("research_project", ResearchProject, ("title", "summary")),
        ("academic_work", AcademicWork, ("title", "abstract")),
        ("scientific_output", ScientificOutput, ("title", "abstract")),
        ("post", Post, ("title", "summary", "content")),
        ("course", Course, ("title", "description")),
        ("transparency_document", TransparencyDocument, ("title", "description")),
    )
    for kind, model, fields in content_models:
        condition = Q()
        for field in fields:
            condition |= Q(**{f"{field}__icontains": query})
        queryset = model.objects.filter(condition, editorial_status=EditorialStatus.PUBLISHED).select_related("unit")
        for item in queryset:
            summary = getattr(item, "summary", "") or getattr(item, "abstract", "") or getattr(item, "description", "")
            add(kind, item.title, item.slug, summary, item.unit)

    partner_condition = Q(name__icontains=query) | Q(description__icontains=query)
    for partner in Partner.objects.filter(partner_condition, is_active=True).prefetch_related("units"):
        units = list(partner.units.all())
        unit = next((item for item in units if not unit_slug or item.slug == unit_slug), None)
        if units and unit:
            add("partner", partner.name, partner.slug, partner.description, unit)

    return results


class GlobalSearchAPIView(APIView):
    """Busca somente conteúdo que já pode ser exibido no portal público."""

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str, required=True),
            OpenApiParameter("type", str, required=False),
            OpenApiParameter("unit", str, required=False),
        ],
        responses={200: OpenApiResponse(description="Resultados públicos da busca")},
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        requested_type = request.query_params.get("type", "").strip()
        unit_slug = request.query_params.get("unit", "").strip()
        results = public_search_results(query, requested_type, unit_slug)
        return Response({"count": len(results), "results": results})

    @staticmethod
    def url_for(kind, slug):
        return search_result_url(kind, slug)
