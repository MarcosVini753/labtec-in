from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.common.admin_scoping import has_active_admin_scope
from apps.common.models import EditorialStatus
from apps.core.models import HeroBanner, InstitutionalSection, SiteSettings
from apps.institutional.models import InstitutionalUnit
from apps.institutional.models import InstitutionMembership
from apps.learning.models import Course
from apps.metrics.models import ImpactMetric
from apps.news.models import Post
from apps.partnerships.models import Partner
from apps.people.models import Person
from apps.portfolio.models import Project
from apps.research.models import AcademicWork, ResearchProject
from apps.scientific.models import ScientificOutput
from apps.transparency.models import TransparencyDocument


def _published(model):
    return model.objects.filter(editorial_status=EditorialStatus.PUBLISHED)


def _public_people_for_unit(unit):
    today = timezone.localdate()
    memberships = InstitutionMembership.objects.filter(
        unit=unit,
        is_active=True,
        is_public=True,
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today),
        Q(end_date__isnull=True) | Q(end_date__gte=today),
    ).select_related("unit")
    return Person.objects.filter(
        is_active=True,
        institution_memberships__in=memberships,
    ).distinct().prefetch_related(
        Prefetch("institution_memberships", queryset=memberships, to_attr="public_unit_memberships"),
    )


def _public_people_for_ecosystem():
    today = timezone.localdate()
    memberships = InstitutionMembership.objects.filter(
        is_active=True,
        is_public=True,
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today),
        Q(end_date__isnull=True) | Q(end_date__gte=today),
    ).select_related("unit")
    return Person.objects.filter(
        is_active=True,
        institution_memberships__in=memberships,
    ).distinct().prefetch_related(
        Prefetch("institution_memberships", queryset=memberships, to_attr="public_unit_memberships"),
    )


def _catalog(request, title, queryset, kind, template="portal/catalog.html"):
    if request.GET.get("q"):
        query = request.GET["q"].strip()
        searchable = {
            "academic_work": "abstract",
            "scientific_output": "abstract",
            "transparency_document": "description",
            "course": "description",
        }.get(kind, "summary")
        queryset = queryset.filter(Q(title__icontains=query) | Q(**{f"{searchable}__icontains": query}))
    context = {"page_title": title, "items": queryset, "kind": kind}
    if request.headers.get("HX-Request"):
        return render(request, "portal/partials/catalog_items.html", context)
    return render(request, template, context)


def home(request):
    root_unit = get_object_or_404(InstitutionalUnit, slug="labtec-in")
    settings = SiteSettings.objects.filter(is_active=True, unit=root_unit).select_related("unit").first()
    hero = HeroBanner.objects.filter(is_published=True, unit=root_unit).select_related("unit").first()
    sections = InstitutionalSection.objects.filter(is_published=True, unit=root_unit).select_related("unit")
    # A Home institucional resume todo conteúdo público do ecossistema;
    # a unidade proprietária continua visível nos cards e nos detalhes.
    projects = _published(Project).select_related("unit", "category").order_by("-published_at", "title")[:6]
    posts = _published(Post).select_related("unit").order_by("-published_at", "title")[:3]
    people = _public_people_for_ecosystem()
    metrics = ImpactMetric.objects.filter(is_active=True, unit__slug="labtec-in")
    return render(request, "portal/home.html", locals())


def unit_detail(request, slug="latec"):
    unit = get_object_or_404(InstitutionalUnit, slug=slug)
    people = _public_people_for_unit(unit)
    return render(request, "portal/unit_detail.html", {
        "unit": unit,
        "sections": unit.institutional_sections.filter(is_published=True),
        "people": people,
        "projects": _published(Project).filter(unit=unit).select_related("unit", "category"),
        "metrics": unit.impact_metrics.filter(is_active=True),
    })


def about(request):
    unit = get_object_or_404(InstitutionalUnit, slug="labtec-in")
    people = _public_people_for_ecosystem()
    return render(request, "portal/about.html", {
        "unit": unit,
        "sections": unit.institutional_sections.filter(is_published=True),
        "people": people,
    })


def portfolio(request):
    return _catalog(request, "Portfólio e projetos", _published(Project).select_related("unit", "category"), "project")


def projects(request):
    return portfolio(request)


def startups(request):
    queryset = _published(Project).filter(category__slug="startup").select_related("unit", "category", "startup_profile")
    return _catalog(request, "Startups", queryset, "project")


def project_detail(request, slug):
    project = get_object_or_404(_published(Project).select_related("unit", "category", "startup_profile"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": project.title, "item": project, "kind": "project"})


def research(request):
    return _catalog(request, "Pesquisas", _published(ResearchProject).select_related("unit"), "research_project")


def research_detail(request, slug):
    item = get_object_or_404(_published(ResearchProject).select_related("unit"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "research_project"})


def academic_works(request):
    queryset = _published(AcademicWork).filter(work_type=AcademicWork.WorkType.TCC).select_related("unit")
    return _catalog(request, "TCCs e trabalhos acadêmicos", queryset, "academic_work")


def academic_work_detail(request, slug):
    item = get_object_or_404(_published(AcademicWork).select_related("unit"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "academic_work"})


def scientific_outputs(request):
    return _catalog(request, "Produção científica", _published(ScientificOutput).select_related("unit"), "scientific_output")


def scientific_output_detail(request, slug):
    item = get_object_or_404(_published(ScientificOutput).select_related("unit"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "scientific_output"})


def transparency(request):
    return _catalog(request, "Transparência", _published(TransparencyDocument).select_related("unit"), "transparency_document")


def transparency_detail(request, slug):
    item = get_object_or_404(_published(TransparencyDocument).select_related("unit"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "transparency_document"})


def news(request):
    return _catalog(request, "Notícias", _published(Post).select_related("unit"), "post")


def news_detail(request, slug):
    item = get_object_or_404(_published(Post).select_related("unit").prefetch_related("links"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "post"})


def courses(request):
    return _catalog(request, "Capacitação", _published(Course).select_related("unit"), "course")


def course_detail(request, slug):
    item = get_object_or_404(_published(Course).select_related("unit"), slug=slug)
    return render(request, "portal/detail.html", {"page_title": item.title, "item": item, "kind": "course"})


def partners(request):
    return render(request, "portal/catalog.html", {"page_title": "Parceiros", "items": Partner.objects.filter(is_active=True), "kind": "partner"})


def contact(request):
    return render(request, "portal/contact.html")


def search(request):
    return render(request, "portal/search.html")


@require_http_methods(["GET", "POST"])
def staff_login(request):
    if request.user.is_authenticated and has_active_admin_scope(request):
        return HttpResponseRedirect(reverse("admin-dashboard"))
    error = None
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            if has_active_admin_scope(request):
                return HttpResponseRedirect(reverse("admin-dashboard"))
            logout(request)
        error = "Usuário ou senha inválidos, ou usuário sem escopo administrativo ativo."
    return render(request, "portal/login.html", {"error": error})


def staff_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("staff-login"))


def admin_dashboard(request):
    if not has_active_admin_scope(request):
        return HttpResponseRedirect(f"{reverse('staff-login')}?next={request.path}")
    unit_slug = request.GET.get("unit", "")
    projects = Project.objects.filter(unit__slug=unit_slug) if unit_slug else Project.objects.all()
    counts = {
        status: projects.filter(editorial_status=status).count()
        for status, _label in EditorialStatus.choices
    }
    context = {
        "counts": counts,
        "units": InstitutionalUnit.objects.order_by("display_order", "name"),
        "selected_unit": unit_slug,
    }
    template = "portal/partials/admin_dashboard_counts.html" if request.headers.get("HX-Request") else "portal/admin_dashboard.html"
    return render(request, template, context)
