from datetime import date, timedelta
import shutil
import tempfile

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.db import IntegrityError, connection, transaction
from django.db.models import Count
from django.db.models.deletion import PROTECT, ProtectedError
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.axes.models import AxisMentorship, ResearchAxis
from apps.common.models import EditorialStatus
from apps.core.models import HeroBanner, InstitutionalSection, SiteSettings, SocialLink
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.learning.models import Course, CourseMaterial
from apps.metrics.models import ImpactMetric
from apps.news.models import Post, PostLink
from apps.partnerships.models import ContactMessage, Partner
from apps.people.models import Person
from apps.portfolio.models import Project, ProjectResult, ProjectStartupProfile, ProjectStatus, ProjectTeamMember
from apps.research.models import AcademicWork, ResearchProject, ResearchProjectMember
from apps.scientific.models import ScientificOutput
from apps.transparency.models import TransparencyDocument


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="latec-test-media-")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CmsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_initial_data", verbosity=0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_seed_rejects_a_database_that_was_already_initialized(self):
        expected_counts = {
            InstitutionalUnit: 2,
            InstitutionMembership: 43,
            Person: 36,
            ResearchAxis: 7,
            AxisMentorship: 9,
            Project: 5,
            ProjectResult: 3,
            ProjectTeamMember: 17,
            ResearchProject: 1,
            ResearchProjectMember: 2,
            Post: 4,
            PostLink: 5,
            Course: 2,
            CourseMaterial: 1,
            ImpactMetric: 6,
            SiteSettings: 1,
            HeroBanner: 1,
            InstitutionalSection: 3,
        }
        with self.assertRaisesMessage(CommandError, "A base já foi inicializada"):
            call_command("seed_initial_data", verbosity=0)
        for model, expected in expected_counts.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(model.objects.count(), expected)

        duplicates = (
            InstitutionMembership.objects.values("person", "unit", "role")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        self.assertFalse(duplicates.exists())
        self.assertFalse(ImpactMetric.objects.filter(key="eventos").exists())
        for app_label, model_name in (
            ("people", "Role"),
            ("news", "PostCategory"),
            ("news", "Tag"),
            ("learning", "LearningTrack"),
            ("learning", "Event"),
        ):
            with self.subTest(model=f"{app_label}.{model_name}"):
                self.assertNotIn(model_name.lower(), django_apps.all_models[app_label])
        self.assertNotIn("mediahub", django_apps.all_models)

    def test_seed_assigns_units_memberships_and_published_research(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        latec = InstitutionalUnit.objects.get(slug="latec")
        self.assertEqual(latec.parent, labtec)
        self.assertEqual(ResearchAxis.objects.filter(unit=latec).count(), 7)
        self.assertEqual(Post.objects.filter(unit=labtec).count(), 3)
        self.assertEqual(Post.objects.filter(unit=latec).count(), 1)
        self.assertFalse(Course.objects.exclude(unit=latec).exists())
        self.assertFalse(Project.objects.exclude(unit=latec).exists())
        self.assertEqual(
            set(Project.objects.values_list("slug", flat=True)),
            {
                "fabrica-de-ensino-bootcamp-de-startups",
                "extensao-em-tecnologias-sustentaveis",
                "farma-amazonia",
                "remedio-vivo",
                "amazon-green-line",
            },
        )
        self.assertEqual(ProjectStartupProfile.objects.count(), 3)
        self.assertEqual(
            set(Post.objects.values_list("slug", flat=True)),
            {
                "coordenadora-da-latec-e-premiada-por-inovacao-tecnologica",
                "latec-participa-do-congresso-nacional-de-inovacao",
                "professora-do-labtec-in-e-homenageada-por-trajetoria-na-nutricao",
                "estagiario-do-labtec-in-participara-de-forum-sobre-internet-no-quenia",
            },
        )
        self.assertEqual(
            set(Course.objects.values_list("slug", flat=True)),
            {"nanotecnologias-de-cosmeticos", "workshop-de-ml-em-biotecnologia"},
        )
        self.assertFalse(ImpactMetric.objects.exclude(unit=labtec).exists())
        self.assertEqual(InstitutionMembership.objects.filter(unit=latec, role="Ligante").count(), 22)
        self.assertEqual(InstitutionMembership.objects.filter(unit=latec, role="Orientador").count(), 9)
        self.assertEqual(InstitutionMembership.objects.count(), 43)
        self.assertFalse(get_user_model().objects.exists())
        self.assertTrue(HeroBanner.objects.get().subtitle.startswith("Um laboratório"))
        self.assertIn(
            "LABTEC.IN e da LATEC",
            Person.objects.get(slug="marta-adelino").short_bio,
        )

        research = ResearchProject.objects.get(slug="pesquisa-de-bioativos-da-amazonia")
        self.assertEqual(research.unit, latec)
        self.assertEqual(research.editorial_status, EditorialStatus.PUBLISHED)
        self.assertFalse(research.file)
        self.assertFalse(research.include_in_parent_ecosystem)
        self.assertFalse(Project.objects.filter(slug=research.slug).exists())
        self.assertFalse(Project.objects.filter(include_in_parent_ecosystem=True).exists())
        self.assertFalse(Post.objects.filter(include_in_parent_ecosystem=True).exists())
        self.assertFalse(Course.objects.filter(include_in_parent_ecosystem=True).exists())

        for slug in Post.objects.values_list("slug", flat=True):
            self.assertEqual(self.client.get(f"/api/v1/posts/{slug}/").status_code, 200)
        marta_response = self.client.get("/api/v1/posts/coordenadora-da-latec-e-premiada-por-inovacao-tecnologica/")
        self.assertEqual(marta_response.json()["unit"]["slug"], "labtec-in")
        self.assertTrue(marta_response.json()["cover_image"].endswith("premioMarta.png"))
        self.assertTrue(marta_response.json()["body_image"].endswith("certificado.png"))
        self.assertEqual(
            marta_response.json()["links"],
            [{
                "label": "5ª edição dos Congressos Brasileiro e Internacional de Educação Empreendedora, Sustentabilidade e Inovação",
                "url": "https://cbae.ufrj.br/2026/05/25/5-congresso-brasileiro-de-educacao-empreendedora-sustentabilidade-e-inovacao/",
                "display_order": 1,
            }],
        )
        gabriel_response = self.client.get("/api/v1/posts/estagiario-do-labtec-in-participara-de-forum-sobre-internet-no-quenia/")
        self.assertEqual(gabriel_response.json()["unit"]["slug"], "labtec-in")
        self.assertTrue(gabriel_response.json()["cover_image"].endswith("gabriel.png"))
        self.assertEqual(len(gabriel_response.json()["links"]), 4)
        material = CourseMaterial.objects.get(title="Apostila de Nanotecnologia")
        self.assertTrue(material.file.name.endswith("Apostila_Nanotecnologia.pdf"))
        self.assertTrue(default_storage.exists(material.file.name))
        for slug in (
            "coordenadora-do-latecin-e-premiada-por-inovacao-tecnologica",
            "latecin-participa-do-congresso-nacional-de-inovacao",
        ):
            self.assertEqual(self.client.get(f"/api/v1/posts/{slug}/").status_code, 404)

    def test_seed_rejection_preserves_manual_choices(self):
        research = ResearchProject.objects.get(slug="pesquisa-de-bioativos-da-amazonia")
        research.editorial_status = EditorialStatus.ARCHIVED
        research.include_in_parent_ecosystem = True
        research.save(update_fields=("editorial_status", "include_in_parent_ecosystem"))
        project = Project.objects.order_by("pk").first()
        project.editorial_status = EditorialStatus.ARCHIVED
        project.include_in_parent_ecosystem = True
        project.save(update_fields=("editorial_status", "include_in_parent_ecosystem"))
        post = Post.objects.get(slug="coordenadora-da-latec-e-premiada-por-inovacao-tecnologica")
        post.editorial_status = EditorialStatus.ARCHIVED
        post.title = "Título alterado manualmente"
        post.content = "Conteúdo alterado manualmente"
        post.cover_image = SimpleUploadedFile("manual.png", b"arquivo-manual", content_type="image/png")
        post.save()
        manual_image_name = post.cover_image.name
        course = Course.objects.order_by("pk").first()
        course.editorial_status = EditorialStatus.ARCHIVED
        course.save(update_fields=("editorial_status",))

        with self.assertRaisesMessage(CommandError, "A base já foi inicializada"):
            call_command("seed_initial_data", verbosity=0)

        research.refresh_from_db()
        project.refresh_from_db()
        post.refresh_from_db()
        course.refresh_from_db()
        self.assertEqual(research.editorial_status, EditorialStatus.ARCHIVED)
        self.assertEqual(project.editorial_status, EditorialStatus.ARCHIVED)
        self.assertEqual(post.editorial_status, EditorialStatus.ARCHIVED)
        self.assertEqual(course.editorial_status, EditorialStatus.ARCHIVED)
        self.assertTrue(research.include_in_parent_ecosystem)
        self.assertTrue(project.include_in_parent_ecosystem)
        self.assertEqual(post.title, "Título alterado manualmente")
        self.assertEqual(post.content, "Conteúdo alterado manualmente")
        self.assertTrue(post.cover_image.name.endswith("manual.png"))
        self.assertTrue(default_storage.exists(manual_image_name))

    def test_home_only_returns_direct_labtec_content(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        latec = InstitutionalUnit.objects.get(slug="latec")
        SiteSettings.objects.create(unit=latec, site_name="LATEC", is_active=True)
        HeroBanner.objects.create(unit=latec, title="Hero LATEC", is_published=True)
        InstitutionalSection.objects.create(
            unit=latec,
            section_type=InstitutionalSection.SectionType.HISTORY,
            title="Seção LATEC",
            slug="secao-latec",
            content="Conteúdo da Liga.",
            is_published=True,
        )
        SocialLink.objects.create(unit=labtec, label="LABTEC.IN", url="https://labtec.example.com")
        SocialLink.objects.create(unit=latec, label="LATEC", url="https://latec.example.com")

        response = self.client.get("/api/v1/site/home/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["settings"]["unit"]["slug"], "labtec-in")
        for collection in ("heroes", "sections", "social_links"):
            self.assertTrue(data[collection])
            self.assertTrue(all(item["unit"]["slug"] == "labtec-in" for item in data[collection]))

    def test_public_workflow_uses_only_editorial_status(self):
        latec = InstitutionalUnit.objects.get(slug="latec")
        execution_status = ProjectStatus.objects.get(slug="arquivado")
        for status in (EditorialStatus.DRAFT, EditorialStatus.IN_REVIEW, EditorialStatus.ARCHIVED):
            Project.objects.create(
                unit=latec,
                title=f"Projeto {status}",
                slug=f"projeto-{status}",
                editorial_status=status,
            )
        published = Project.objects.create(
            unit=latec,
            title="Projeto publicado",
            slug="projeto-publicado-workflow",
            status=execution_status,
            editorial_status=EditorialStatus.PUBLISHED,
        )

        response = self.client.get("/api/v1/projects/")
        slugs = {item["slug"] for item in response.json()["results"]}
        self.assertIn(published.slug, slugs)
        self.assertTrue({"projeto-draft", "projeto-in_review", "projeto-archived"}.isdisjoint(slugs))
        item = next(item for item in response.json()["results"] if item["slug"] == published.slug)
        self.assertTrue({"is_published", "is_featured", "display_order"}.isdisjoint(item))
        filtered = self.client.get("/api/v1/projects/", {"status": execution_status.slug})
        self.assertIn(published.slug, {item["slug"] for item in filtered.json()["results"]})

    def test_units_are_inherently_public_and_parent_is_always_serialized(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        unit = InstitutionalUnit.objects.create(
            name="Unidade pública",
            acronym="UP",
            slug="unidade-publica",
            unit_type=InstitutionalUnit.UnitType.INITIATIVE,
            parent=labtec,
        )

        response = self.client.get("/api/v1/institutional-units/")

        self.assertEqual(response.status_code, 200)
        item = next(item for item in response.json()["results"] if item["slug"] == unit.slug)
        self.assertEqual(item["parent"]["slug"], labtec.slug)
        self.assertTrue({"is_active", "is_public"}.isdisjoint(item))
        self.assertTrue({"is_active", "is_public"}.isdisjoint(
            field.name for field in InstitutionalUnit._meta.fields
        ))

    def test_published_course_exposes_every_material_and_draft_course_is_hidden(self):
        self.assertNotIn("is_public", {field.name for field in CourseMaterial._meta.fields})
        course = Course.objects.get(slug="nanotecnologias-de-cosmeticos")

        response = self.client.get(f"/api/v1/courses/{course.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [material["title"] for material in response.json()["materials"]],
            ["Apostila de Nanotecnologia"],
        )

        draft = Course.objects.create(
            unit=course.unit,
            title="Curso em rascunho",
            slug="curso-em-rascunho",
            editorial_status=EditorialStatus.DRAFT,
        )
        CourseMaterial.objects.create(course=draft, title="Material do rascunho")
        self.assertEqual(self.client.get(f"/api/v1/courses/{draft.slug}/").status_code, 404)

    def test_unit_filter_aggregates_only_opted_direct_children(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        latec = InstitutionalUnit.objects.get(slug="latec")
        grandchild = InstitutionalUnit.objects.create(
            name="Núcleo",
            acronym="N",
            slug="nucleo",
            unit_type=InstitutionalUnit.UnitType.INITIATIVE,
            parent=latec,
        )
        own = Project.objects.create(
            unit=labtec,
            title="Projeto raiz",
            slug="projeto-raiz",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        opted = Project.objects.create(
            unit=latec,
            title="Projeto filho optante",
            slug="projeto-filho-optante",
            editorial_status=EditorialStatus.PUBLISHED,
            include_in_parent_ecosystem=True,
        )
        direct = Project.objects.create(
            unit=latec,
            title="Projeto filho direto",
            slug="projeto-filho-direto",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        nested = Project.objects.create(
            unit=grandchild,
            title="Projeto neto optante",
            slug="projeto-neto-optante",
            editorial_status=EditorialStatus.PUBLISHED,
            include_in_parent_ecosystem=True,
        )

        root_items = self.client.get("/api/v1/projects/", {"unit": "labtec-in"}).json()["results"]
        root_slugs = {item["slug"] for item in root_items}
        self.assertIn(own.slug, root_slugs)
        self.assertIn(opted.slug, root_slugs)
        self.assertNotIn(direct.slug, root_slugs)
        self.assertNotIn(nested.slug, root_slugs)
        opted_item = next(item for item in root_items if item["slug"] == opted.slug)
        self.assertEqual(opted_item["unit"]["slug"], "latec")

        latec_slugs = {
            item["slug"]
            for item in self.client.get("/api/v1/projects/", {"unit": "latec"}).json()["results"]
        }
        self.assertTrue({opted.slug, direct.slug, nested.slug}.issubset(latec_slugs))
        all_slugs = {item["slug"] for item in self.client.get("/api/v1/projects/").json()["results"]}
        self.assertTrue({own.slug, opted.slug, direct.slug, nested.slug}.issubset(all_slugs))

    def test_ecosystem_filter_applies_to_all_seven_editorial_endpoints(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        latec = InstitutionalUnit.objects.get(slug="latec")
        common = {
            "unit": latec,
            "editorial_status": EditorialStatus.PUBLISHED,
            "include_in_parent_ecosystem": True,
        }
        records = [
            ("projects", Project.objects.create(title="Projeto agregado", slug="projeto-agregado", **common)),
            ("posts", Post.objects.create(title="Post agregado", slug="post-agregado", content="Texto", **common)),
            ("courses", Course.objects.create(title="Curso agregado", slug="curso-agregado", **common)),
            (
                "research-projects",
                ResearchProject.objects.create(title="Pesquisa agregada", slug="pesquisa-agregada", **common),
            ),
            (
                "academic-works",
                AcademicWork.objects.create(
                    title="Trabalho agregado",
                    slug="trabalho-agregado",
                    work_type=AcademicWork.WorkType.TCC,
                    **common,
                ),
            ),
            (
                "scientific-outputs",
                ScientificOutput.objects.create(
                    title="Produção agregada",
                    slug="producao-agregada",
                    output_type=ScientificOutput.OutputType.ARTICLE,
                    **common,
                ),
            ),
        ]
        records.append(
            (
                "transparency-documents",
                TransparencyDocument.objects.create(
                    title="Documento agregado",
                    slug="documento-agregado",
                    document_type=TransparencyDocument.DocumentType.STATEMENT,
                    file=SimpleUploadedFile("documento.pdf", b"pdf"),
                    **common,
                ),
            )
        )
        for endpoint, record in records:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(f"/api/v1/{endpoint}/", {"unit": labtec.slug})
                self.assertEqual(response.status_code, 200)
                item = next(
                    item
                    for item in response.json()["results"]
                    if item["slug"] == record.slug
                )
                self.assertTrue(
                    {"editorial_status", "include_in_parent_ecosystem", "is_published", "is_featured", "display_order"}.isdisjoint(item)
                )

        removed_fields = {
            "projects": set(),
            "posts": {"category", "tags", "authors"},
            "courses": {"track"},
            "research-projects": {"objectives", "methodology", "expected_results", "cover_image"},
            "academic-works": set(),
            "scientific-outputs": {"authors"},
            "transparency-documents": set(),
        }
        for endpoint, record in records:
            item = self.client.get(f"/api/v1/{endpoint}/{record.slug}/").json()
            self.assertTrue(removed_fields[endpoint].isdisjoint(item))

    def test_people_expose_only_current_public_memberships_without_n_plus_one(self):
        labtec = InstitutionalUnit.objects.get(slug="labtec-in")
        person = Person.objects.create(full_name="Pessoa pública", slug="pessoa-publica")
        today = timezone.localdate()
        InstitutionMembership.objects.create(person=person, unit=labtec, role="Pesquisador")
        InstitutionMembership.objects.create(person=person, unit=labtec, role="Privado", is_public=False)
        InstitutionMembership.objects.create(person=person, unit=labtec, role="Inativo", is_active=False)
        InstitutionMembership.objects.create(
            person=person,
            unit=labtec,
            role="Futuro",
            start_date=today + timedelta(days=1),
        )
        InstitutionMembership.objects.create(
            person=person,
            unit=labtec,
            role="Encerrado",
            end_date=today - timedelta(days=1),
        )
        with CaptureQueriesContext(connection) as first_queries:
            response = self.client.get(f"/api/v1/people/{person.slug}/")
        item = response.json()
        self.assertTrue({"role", "is_featured"}.isdisjoint(item))
        self.assertEqual(item["memberships"], [{
            "unit": {"name": labtec.name, "acronym": labtec.acronym, "slug": labtec.slug, "unit_type": labtec.unit_type},
            "role": "Pesquisador",
        }])

        second = Person.objects.create(full_name="Outra pessoa", slug="outra-pessoa")
        InstitutionMembership.objects.create(person=second, unit=labtec, role="Pesquisador")
        with CaptureQueriesContext(connection) as second_queries:
            self.client.get("/api/v1/people/")
        with CaptureQueriesContext(connection) as third_queries:
            Person.objects.create(full_name="Terceira pessoa", slug="terceira-pessoa")
            self.client.get("/api/v1/people/")
        self.assertEqual(len(second_queries), len(third_queries) - 1)
        self.assertLessEqual(len(first_queries), 4)

    def test_nested_public_endpoints_do_not_add_queries_per_item(self):
        latec = InstitutionalUnit.objects.get(slug="latec")
        axis = ResearchAxis.objects.filter(unit=latec).first()
        person = Person.objects.first()
        first_partner = Partner.objects.create(name="Parceiro inicial", slug="parceiro-inicial")
        first_partner.units.add(latec)
        Project.objects.order_by("pk").update(axis=axis)
        Post.objects.order_by("pk").update(axis=axis)
        Course.objects.order_by("pk").update(axis=axis)
        endpoints = ("axes", "projects", "posts", "courses", "partners")

        for endpoint in endpoints:
            self.client.get(f"/api/v1/{endpoint}/")
        initial = {}
        for endpoint in endpoints:
            with CaptureQueriesContext(connection) as queries:
                self.client.get(f"/api/v1/{endpoint}/")
            initial[endpoint] = len(queries)

        new_axis = ResearchAxis.objects.create(
            unit=latec,
            number=99,
            title="Eixo adicional",
            slug="eixo-adicional",
        )
        AxisMentorship.objects.create(axis=new_axis, person=person)
        project = Project.objects.create(
            unit=latec,
            axis=axis,
            title="Projeto adicional",
            slug="projeto-adicional",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        ProjectTeamMember.objects.create(project=project, person=person)
        ProjectResult.objects.create(project=project, title="Resultado adicional")
        Post.objects.create(
            unit=latec,
            axis=axis,
            title="Post adicional",
            slug="post-adicional",
            content="Conteúdo",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        course = Course.objects.create(
            unit=latec,
            axis=axis,
            title="Curso adicional",
            slug="curso-adicional",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        course.instructors.add(person)
        CourseMaterial.objects.create(course=course, title="Material adicional")
        second_partner = Partner.objects.create(name="Parceiro adicional", slug="parceiro-adicional")
        second_partner.units.add(latec)

        for endpoint, query_count in initial.items():
            with self.subTest(endpoint=endpoint), CaptureQueriesContext(connection) as queries:
                self.client.get(f"/api/v1/{endpoint}/")
            self.assertEqual(len(queries), query_count, endpoint)

    def test_unit_is_required_and_protected(self):
        unit_models = (
            SiteSettings,
            HeroBanner,
            InstitutionalSection,
            SocialLink,
            ResearchAxis,
            Project,
            Post,
            Course,
            ResearchProject,
            AcademicWork,
            ScientificOutput,
            TransparencyDocument,
            ImpactMetric,
        )
        for model in unit_models:
            with self.subTest(model=model.__name__):
                field = model._meta.get_field("unit")
                self.assertFalse(field.null)
                self.assertIs(field.remote_field.on_delete, PROTECT)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Project.objects.create(title="Sem unidade", slug="sem-unidade")
        latec = InstitutionalUnit.objects.get(slug="latec")
        with self.assertRaises(ProtectedError):
            latec.delete()

    def test_public_endpoints_and_removed_tag_route(self):
        urls = (
            "/api/v1/site/home/",
            "/api/v1/site/settings/",
            "/api/v1/institutional-units/",
            "/api/v1/people/",
            "/api/v1/axes/",
            "/api/v1/projects/",
            "/api/v1/research-projects/",
            "/api/v1/academic-works/",
            "/api/v1/scientific-outputs/",
            "/api/v1/posts/",
            "/api/v1/courses/",
            "/api/v1/transparency-documents/",
            "/api/v1/partners/",
            "/api/v1/metrics/impact/",
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/posts/tags/").status_code, 404)

    def test_partner_multi_unit_and_contact_creation_still_work(self):
        units = list(InstitutionalUnit.objects.filter(slug__in=("labtec-in", "latec")))
        partner = Partner.objects.create(name="UFAC", slug="ufac")
        partner.units.add(*units)
        for unit in units:
            response = self.client.get("/api/v1/partners/", {"unit": unit.slug})
            self.assertIn(partner.slug, {item["slug"] for item in response.json()["results"]})
        response = self.client.post(
            "/api/v1/contact/",
            {
                "contact_type": "partnership",
                "subject": "Parceria institucional",
                "name": "Pessoa Interessada",
                "email": "pessoa@example.com",
                "message": "Gostaria de conversar sobre uma parceria.",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_openapi_reflects_the_simplified_contract(self):
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")
        schema_text = response.content.decode()
        schema = response.json()
        self.assertIn("/api/v1/research-projects/", schema["paths"])
        self.assertIn("/api/v1/academic-works/", schema["paths"])
        self.assertNotIn("/api/v1/posts/tags/", schema["paths"])
        self.assertNotIn('"featured"', schema_text)
        self.assertTrue(
            {"is_active", "is_public"}.isdisjoint(
                schema["components"]["schemas"]["InstitutionalUnit"]["properties"]
            )
        )

        filters = {
            "projects": {"unit", "axis", "category", "status", "year", "search"},
            "posts": {"unit", "axis", "year", "search"},
            "courses": {"unit", "axis", "year", "search"},
            "research-projects": {"unit", "axis", "project_status", "year", "search"},
            "academic-works": {"unit", "work_type", "year", "search"},
            "scientific-outputs": {"unit", "axis", "year", "search"},
            "transparency-documents": {"unit", "year", "search"},
        }
        for endpoint, expected in filters.items():
            with self.subTest(endpoint=endpoint):
                parameters = {
                    item["name"]: item
                    for item in schema["paths"][f"/api/v1/{endpoint}/"]["get"]["parameters"]
                }
                self.assertTrue(expected.issubset(parameters))
                self.assertIn("filhas diretas", parameters["unit"]["description"])


class SeedBootstrapValidationTests(TestCase):
    def test_missing_canonical_asset_prevents_bootstrap(self):
        with tempfile.TemporaryDirectory(prefix="latec-missing-seed-assets-") as seed_assets_root:
            with override_settings(SEED_ASSETS_ROOT=seed_assets_root):
                with self.assertRaisesMessage(CommandError, "Ativos canônicos ausentes"):
                    call_command("seed_initial_data", verbosity=0)

        self.assertFalse(InstitutionalUnit.objects.filter(slug="labtec-in").exists())
