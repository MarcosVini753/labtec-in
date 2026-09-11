from django.contrib import admin, messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.common.admin_scoping import get_admin_profile, has_active_admin_scope, is_global_admin
from apps.common.models import EditorialStatus
from apps.common.search import public_search_results
from apps.core.models import HeroBanner, InstitutionalSection, SiteSettings
from apps.institutional.models import InstitutionalUnit
from apps.institutional.models import InstitutionMembership
from apps.learning.models import Course
from apps.metrics.models import ImpactMetric
from apps.news.models import Post
from apps.partnerships.models import Partner
from apps.partnerships.serializers import ContactMessageSerializer
from apps.people.models import Person
from apps.portfolio.models import Project
from apps.research.models import AcademicWork, ResearchProject
from apps.scientific.models import ScientificOutput
from apps.transparency.models import TransparencyDocument


ADMIN_SCOPE_ERROR = (
    "Sua conta foi autenticada, mas não possui um perfil administrativo ativo e válido. "
    "Solicite a configuração do papel e da unidade."
)


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
    if request.GET.get("q") is not None:
        return HttpResponseRedirect(f"{reverse('projects')}?{request.GET.urlencode()}")
    return render(request, "portal/portfolio.html")


def projects(request):
    return _catalog(request, "Projetos", _published(Project).select_related("unit", "category"), "project")


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
    queryset = _published(AcademicWork).select_related("unit")
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


@require_http_methods(["GET", "POST"])
def contact(request):
    context = {}
    if request.method == "POST":
        serializer = ContactMessageSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            if request.headers.get("HX-Request"):
                return render(request, "portal/partials/contact_feedback.html", {"success": True}, status=201)
            messages.success(request, "Mensagem enviada com sucesso.")
            return HttpResponseRedirect(reverse("contact"))
        context = {"errors": serializer.errors, "form_data": request.POST}
        if request.headers.get("HX-Request"):
            return render(request, "portal/partials/contact_feedback.html", context)
    return render(request, "portal/contact.html", context, status=400 if context else 200)


def search(request):
    query = request.GET.get("q", "").strip()
    context = {"query": query, "results": public_search_results(query)}
    if request.headers.get("HX-Request"):
        return render(request, "portal/partials/search_results.html", context)
    return render(request, "portal/search.html", context)


@require_http_methods(["GET", "POST"])
def staff_login(request):
    if request.user.is_authenticated and has_active_admin_scope(request):
        return HttpResponseRedirect(reverse("admin-dashboard"))
    error = ADMIN_SCOPE_ERROR if request.GET.get("reason") == "admin-scope" else None
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            if has_active_admin_scope(request):
                return HttpResponseRedirect(reverse("admin-dashboard"))
            logout(request)
            error = ADMIN_SCOPE_ERROR
        else:
            error = "Usuário ou senha inválidos."
    return render(request, "portal/login.html", {"error": error})


def staff_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("staff-login"))


EDITORIAL_MODELS = (
    Project,
    ResearchProject,
    AcademicWork,
    ScientificOutput,
    Post,
    Course,
    TransparencyDocument,
)


def admin_dashboard(request):
    if not has_active_admin_scope(request):
        return HttpResponseRedirect(f"{reverse('staff-login')}?next={request.path}")
    global_admin = is_global_admin(request)
    if global_admin:
        units = InstitutionalUnit.objects.order_by("display_order", "name")
    else:
        profile = get_admin_profile(request)
        units = InstitutionalUnit.objects.filter(pk__in=profile.accessible_unit_ids()).order_by("display_order", "name")
    unit_slug = request.GET.get("unit", "")
    # ponytail: slug inválido/fora do escopo cai silenciosamente no escopo completo; upgrade: mensagem inline.
    if unit_slug and not units.filter(slug=unit_slug).exists():
        unit_slug = ""
    selected_unit = units.filter(slug=unit_slug).first() if unit_slug else None
    unit_filter = f"&unit__id__exact={selected_unit.pk}" if selected_unit else ""

    status_choices = list(EditorialStatus.choices)
    totals = {status: 0 for status, _label in status_choices}
    rows = []
    for model in EDITORIAL_MODELS:
        modeladmin = admin.site._registry.get(model)
        if modeladmin is None:
            continue
        # Mesmo queryset do Admin: escopo por unidade, eixo do orientador e nível de acesso.
        scoped = modeladmin.get_queryset(request)
        if selected_unit:
            scoped = scoped.filter(unit=selected_unit)
        per_status = dict(scoped.values_list("editorial_status").annotate(total=Count("id")))
        if not any(per_status.values()):
            continue
        changelist = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")
        cells = []
        for status, label in status_choices:
            count = per_status.get(status, 0)
            totals[status] += count
            cells.append({
                "status": status,
                "label": label,
                "count": count,
                "url": f"{changelist}?editorial_status__exact={status}{unit_filter}",
            })
        rows.append({
            "label": model._meta.verbose_name_plural,
            "cells": cells,
            "total": sum(cell["count"] for cell in cells),
        })
    context = {
        "totals": [
            {"status": status, "label": label, "count": totals[status]}
            for status, label in status_choices
        ],
        "rows": rows,
        "units": units,
        "selected_unit": unit_slug,
        "all_units_label": "Todas" if global_admin else "Todas as minhas unidades",
    }
    template = "portal/partials/admin_dashboard_counts.html" if request.headers.get("HX-Request") else "portal/admin_dashboard.html"
    return render(request, template, context)
