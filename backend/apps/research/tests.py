from datetime import date
from importlib import import_module
import shutil
import tempfile
from types import SimpleNamespace

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.accounts.models import Profile
from apps.axes.models import ResearchAxis
from apps.common.models import EditorialStatus
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.people.models import Person
from apps.research.admin import (
    AcademicWorkAdmin,
    AcademicWorkContributorAdmin,
    ResearchProjectAdmin,
    ResearchProjectMemberAdmin,
)
from apps.research.models import AcademicWork, AcademicWorkContributor, ResearchProject, ResearchProjectMember
from apps.scientific.admin import ScientificAuthorshipAdmin, ScientificOutputAdmin
from apps.scientific.models import ScientificAuthorship, ScientificOutput


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="latec-research-test-media-")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ResearchDomainTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.labtec = InstitutionalUnit.objects.create(
            name="LABTEC.IN",
            acronym="LABTEC.IN",
            slug="labtec-in-test",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )
        cls.latec = InstitutionalUnit.objects.create(
            name="LATEC",
            acronym="LATEC",
            slug="latec-test",
            unit_type=InstitutionalUnit.UnitType.ACADEMIC_LEAGUE,
            parent=cls.labtec,
        )
        cls.axis = ResearchAxis.objects.create(
            unit=cls.latec,
            number=99,
            title="Eixo de testes",
            slug="eixo-de-testes",
        )
        cls.person = Person.objects.create(full_name="Ana Pesquisadora", slug="ana-pesquisadora")
        InstitutionMembership.objects.create(person=cls.person, unit=cls.labtec, role="Pesquisador")
        cls.research_project = ResearchProject.objects.create(
            unit=cls.labtec,
            axis=cls.axis,
            title="Pesquisa publicada",
            slug="pesquisa-publicada",
            summary="Bioativos amazônicos.",
            file=SimpleUploadedFile("pesquisa.pdf", b"pesquisa"),
            external_url="https://example.com/pesquisa",
            start_date=date(2026, 2, 1),
            project_status=ResearchProject.ProjectStatus.IN_PROGRESS,
            editorial_status=EditorialStatus.PUBLISHED,
        )
        ResearchProjectMember.objects.create(
            research_project=cls.research_project,
            person=cls.person,
            role=ResearchProjectMember.Role.COORDINATOR,
            display_order=1,
        )
        cls.academic_work = AcademicWork.objects.create(
            unit=cls.labtec,
            research_project=cls.research_project,
            title="TCC publicado",
            slug="tcc-publicado",
            work_type=AcademicWork.WorkType.TCC,
            course="Biotecnologia",
            institution="UFAC",
            year=2026,
            abstract="Trabalho sobre bioativos.",
            keywords="bioativos, Amazônia",
            file=SimpleUploadedFile("tcc.pdf", b"tcc"),
            external_url="https://example.com/tcc",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        AcademicWorkContributor.objects.create(
            academic_work=cls.academic_work,
            person=cls.person,
            role=AcademicWorkContributor.Role.AUTHOR,
            display_order=1,
        )
        cls.scientific_output = ScientificOutput.objects.create(
            unit=cls.labtec,
            axis=cls.axis,
            research_project=cls.research_project,
            academic_work=cls.academic_work,
            title="Artigo publicado",
            slug="artigo-publicado",
            output_type=ScientificOutput.OutputType.ARTICLE,
            abstract="Resumo publicado.",
            publication_date=date(2026, 3, 1),
            file=SimpleUploadedFile("artigo.pdf", b"artigo"),
            external_url="https://example.com/artigo",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        ScientificAuthorship.objects.create(
            scientific_output=cls.scientific_output,
            person=cls.person,
            author_order=1,
            author_role="Autora principal",
        )
        ResearchProject.objects.create(
            unit=cls.latec,
            title="Pesquisa em rascunho",
            slug="pesquisa-em-rascunho",
        )
        AcademicWork.objects.create(
            unit=cls.latec,
            title="Trabalho em rascunho",
            slug="trabalho-em-rascunho",
            work_type=AcademicWork.WorkType.OTHER,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_date_range_and_relational_constraints(self):
        invalid = ResearchProject(
            unit=self.labtec,
            title="Datas inválidas",
            slug="datas-invalidas",
            start_date=date(2026, 2, 2),
            end_date=date(2026, 2, 1),
        )
        with self.assertRaisesMessage(ValidationError, "igual ou posterior"):
            invalid.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            ResearchProject.objects.create(
                unit=self.labtec,
                title="Constraint de datas",
                slug="constraint-de-datas",
                start_date=date(2026, 2, 2),
                end_date=date(2026, 2, 1),
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ResearchProjectMember.objects.create(
                research_project=self.research_project,
                person=self.person,
                role=ResearchProjectMember.Role.RESEARCHER,
            )
        with self.assertRaises(ProtectedError):
            self.labtec.delete()

    def test_research_endpoint_filters_and_returns_minimal_file_metadata(self):
        response = self.client.get(
            "/api/v1/research-projects/",
            {
                "unit": self.labtec.slug,
                "axis": self.axis.slug,
                "project_status": ResearchProject.ProjectStatus.IN_PROGRESS,
                "year": 2026,
                "search": "Bioativos",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["slug"] for item in response.json()["results"]], [self.research_project.slug])
        item = response.json()["results"][0]
        self.assertTrue(item["file"].endswith(self.research_project.file.url))
        self.assertEqual(item["external_url"], "https://example.com/pesquisa")
        self.assertTrue({"objectives", "methodology", "expected_results", "cover_image"}.isdisjoint(item))
        self.assertEqual(item["team_members"][0]["role"], ResearchProjectMember.Role.COORDINATOR)
        self.assertNotIn("is_coordinator", item["team_members"][0])
        self.assertNotIn("memberships", item["team_members"][0]["person"])
        self.assertEqual(self.client.get("/api/v1/research-projects/pesquisa-em-rascunho/").status_code, 404)

    def test_academic_work_and_scientific_output_return_structured_relations(self):
        work_response = self.client.get(
            "/api/v1/academic-works/",
            {"unit": self.labtec.slug, "work_type": AcademicWork.WorkType.TCC, "year": 2026, "search": "bioativos"},
        )
        work = work_response.json()["results"][0]
        self.assertEqual(work["research_project"]["slug"], self.research_project.slug)
        self.assertEqual(work["contributors"][0]["person"]["slug"], self.person.slug)
        self.assertTrue(work["file"].endswith(self.academic_work.file.url))
        self.assertEqual(self.client.get("/api/v1/academic-works/trabalho-em-rascunho/").status_code, 404)

        output = self.client.get(f"/api/v1/scientific-outputs/{self.scientific_output.slug}/").json()
        self.assertNotIn("authors", output)
        self.assertEqual(output["authorships"][0]["person"]["slug"], self.person.slug)
        self.assertEqual(output["research_project"]["slug"], self.research_project.slug)
        self.assertEqual(output["academic_work"]["slug"], self.academic_work.slug)
        self.assertTrue(output["file"].endswith(self.scientific_output.file.url))

    def test_public_relations_hide_unpublished_records(self):
        hidden_outputs = []
        for status in (EditorialStatus.DRAFT, EditorialStatus.IN_REVIEW, EditorialStatus.ARCHIVED):
            project = ResearchProject.objects.create(
                unit=self.labtec,
                title=f"Pesquisa {status}",
                slug=f"pesquisa-{status}",
                editorial_status=status,
            )
            hidden_outputs.append(
                ScientificOutput.objects.create(
                    unit=self.labtec,
                    research_project=project,
                    title=f"Artigo da pesquisa {status}",
                    slug=f"artigo-pesquisa-{status}",
                    output_type=ScientificOutput.OutputType.ARTICLE,
                    editorial_status=EditorialStatus.PUBLISHED,
                )
            )

        hidden_work = AcademicWork.objects.create(
            unit=self.labtec,
            title="Trabalho em rascunho vinculado",
            slug="trabalho-em-rascunho-vinculado",
            work_type=AcademicWork.WorkType.OTHER,
        )
        output_with_hidden_work = ScientificOutput.objects.create(
            unit=self.labtec,
            research_project=self.research_project,
            academic_work=hidden_work,
            title="Artigo com trabalho em rascunho",
            slug="artigo-com-trabalho-em-rascunho",
            output_type=ScientificOutput.OutputType.ARTICLE,
            editorial_status=EditorialStatus.PUBLISHED,
        )
        work_with_hidden_project = AcademicWork.objects.create(
            unit=self.labtec,
            research_project=hidden_outputs[0].research_project,
            title="TCC com pesquisa em rascunho",
            slug="tcc-com-pesquisa-em-rascunho",
            work_type=AcademicWork.WorkType.TCC,
            editorial_status=EditorialStatus.PUBLISHED,
        )

        output_by_slug = {
            item["slug"]: item
            for item in self.client.get("/api/v1/scientific-outputs/").json()["results"]
        }
        for output in hidden_outputs:
            self.assertIsNone(output_by_slug[output.slug]["research_project"])
        self.assertIsNone(output_by_slug[output_with_hidden_work.slug]["academic_work"])

        hidden_project_detail = self.client.get(
            f"/api/v1/scientific-outputs/{hidden_outputs[0].slug}/"
        ).json()
        self.assertIsNone(hidden_project_detail["research_project"])
        output_detail = self.client.get(
            f"/api/v1/scientific-outputs/{output_with_hidden_work.slug}/"
        ).json()
        self.assertIsNone(output_detail["academic_work"])

        work_by_slug = {
            item["slug"]: item for item in self.client.get("/api/v1/academic-works/").json()["results"]
        }
        self.assertIsNone(work_by_slug[work_with_hidden_project.slug]["research_project"])
        work_detail = self.client.get(f"/api/v1/academic-works/{work_with_hidden_project.slug}/").json()
        self.assertIsNone(work_detail["research_project"])

    def test_invalid_year_returns_400_and_featured_is_absent_from_openapi(self):
        for endpoint in ("research-projects", "academic-works", "scientific-outputs"):
            self.assertEqual(self.client.get(f"/api/v1/{endpoint}/", {"year": "abc"}).status_code, 400)
        schema = self.client.get("/api/schema/").content.decode()
        self.assertIn("project_status", schema)
        self.assertIn("work_type", schema)
        self.assertNotIn("name: featured", schema)

    def test_nested_endpoints_do_not_add_queries_per_item(self):
        initial = {}
        for endpoint in ("research-projects", "academic-works", "scientific-outputs"):
            with CaptureQueriesContext(connection) as queries:
                self.client.get(f"/api/v1/{endpoint}/")
            initial[endpoint] = len(queries)

        person = Person.objects.create(full_name="Bia Pesquisadora", slug="bia-pesquisadora")
        research = ResearchProject.objects.create(
            unit=self.labtec,
            title="Segunda pesquisa",
            slug="segunda-pesquisa",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        ResearchProjectMember.objects.create(research_project=research, person=person)
        work = AcademicWork.objects.create(
            unit=self.labtec,
            research_project=research,
            title="Segundo trabalho",
            slug="segundo-trabalho",
            work_type=AcademicWork.WorkType.OTHER,
            editorial_status=EditorialStatus.PUBLISHED,
        )
        AcademicWorkContributor.objects.create(
            academic_work=work,
            person=person,
            role=AcademicWorkContributor.Role.AUTHOR,
        )
        output = ScientificOutput.objects.create(
            unit=self.labtec,
            research_project=research,
            academic_work=work,
            title="Segundo artigo",
            slug="segundo-artigo",
            output_type=ScientificOutput.OutputType.ARTICLE,
            editorial_status=EditorialStatus.PUBLISHED,
        )
        ScientificAuthorship.objects.create(scientific_output=output, person=person, author_order=1)

        for endpoint, query_count in initial.items():
            with self.subTest(endpoint=endpoint), CaptureQueriesContext(connection) as queries:
                self.client.get(f"/api/v1/{endpoint}/")
            self.assertEqual(len(queries), query_count)


class ResearchAdminScopeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.labtec = InstitutionalUnit.objects.create(
            name="LABTEC.IN",
            acronym="LABTEC.IN",
            slug="labtec-in-admin",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )
        cls.latec = InstitutionalUnit.objects.create(
            name="LATEC",
            acronym="LATEC",
            slug="latec",
            unit_type=InstitutionalUnit.UnitType.ACADEMIC_LEAGUE,
            parent=cls.labtec,
        )
        cls.axis = ResearchAxis.objects.create(unit=cls.latec, number=201, title="Eixo permitido", slug="eixo-permitido")
        cls.other_axis = ResearchAxis.objects.create(unit=cls.latec, number=202, title="Outro eixo", slug="outro-eixo-admin")
        cls.person = Person.objects.create(full_name="Pessoa do Admin", slug="pessoa-do-admin")
        cls.mentor_person = Person.objects.create(full_name="Mentora do Admin", slug="mentora-do-admin")
        InstitutionMembership.objects.create(person=cls.person, unit=cls.latec, role="Pesquisador")
        InstitutionMembership.objects.create(person=cls.mentor_person, unit=cls.latec, role="Orientador")
        cls.axis.mentorships.create(person=cls.mentor_person)
        cls.coordinator_user = get_user_model().objects.create_user("unit_coordinator", is_staff=True)
        Profile.objects.create(
            user=cls.coordinator_user,
            role=Profile.AdminRole.UNIT_COORDINATOR,
            primary_unit=cls.latec,
        )
        cls.mentor_user = get_user_model().objects.create_user("research_mentor", is_staff=True)
        Profile.objects.create(
            user=cls.mentor_user,
            person=cls.mentor_person,
            role=Profile.AdminRole.MENTOR,
            primary_unit=cls.latec,
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.post("/admin/")
        self.request.user = self.coordinator_user

    def test_unit_coordinator_creates_full_research_graph_as_draft(self):
        project_admin = ResearchProjectAdmin(ResearchProject, admin.site)
        member_admin = ResearchProjectMemberAdmin(ResearchProjectMember, admin.site)
        work_admin = AcademicWorkAdmin(AcademicWork, admin.site)
        contributor_admin = AcademicWorkContributorAdmin(AcademicWorkContributor, admin.site)
        output_admin = ScientificOutputAdmin(ScientificOutput, admin.site)
        authorship_admin = ScientificAuthorshipAdmin(ScientificAuthorship, admin.site)

        project = ResearchProject(
            unit=self.latec,
            axis=self.axis,
            title="Pesquisa criada no Admin",
            slug="pesquisa-criada-no-admin",
            include_in_parent_ecosystem=True,
        )
        project_admin.save_model(self.request, project, form=None, change=False)
        member = ResearchProjectMember(research_project=project, person=self.person)
        member_admin.save_model(self.request, member, form=None, change=False)
        work = AcademicWork(
            unit=self.latec,
            research_project=project,
            title="Trabalho criado no Admin",
            slug="trabalho-criado-no-admin",
            work_type=AcademicWork.WorkType.TCC,
        )
        work_admin.save_model(self.request, work, form=None, change=False)
        contributor = AcademicWorkContributor(
            academic_work=work,
            person=self.person,
            role=AcademicWorkContributor.Role.AUTHOR,
        )
        contributor_admin.save_model(self.request, contributor, form=None, change=False)
        output = ScientificOutput(
            unit=self.latec,
            axis=self.axis,
            research_project=project,
            academic_work=work,
            title="Produção criada no Admin",
            slug="producao-criada-no-admin",
            output_type=ScientificOutput.OutputType.ARTICLE,
        )
        output_admin.save_model(self.request, output, form=None, change=False)
        authorship = ScientificAuthorship(scientific_output=output, person=self.person, author_order=1)
        authorship_admin.save_model(self.request, authorship, form=None, change=False)

        self.assertEqual(project.editorial_status, EditorialStatus.DRAFT)
        self.assertTrue(project.include_in_parent_ecosystem)
        self.assertTrue(authorship_admin.get_queryset(self.request).filter(pk=authorship.pk).exists())

    def test_mentor_is_limited_to_own_axis(self):
        own = ResearchProject.objects.create(unit=self.latec, axis=self.axis, title="Pesquisa própria", slug="pesquisa-propria")
        ResearchProject.objects.create(unit=self.latec, axis=self.other_axis, title="Pesquisa externa", slug="pesquisa-externa")
        request = self.factory.post("/admin/")
        request.user = self.mentor_user
        project_admin = ResearchProjectAdmin(ResearchProject, admin.site)
        self.assertEqual(set(project_admin.get_queryset(request).values_list("slug", flat=True)), {own.slug})

        allowed = ResearchProject(
            unit=self.latec,
            axis=self.axis,
            title="Pesquisa criada pela mentora",
            slug="pesquisa-criada-pela-mentora",
            include_in_parent_ecosystem=True,
        )
        project_admin.save_model(request, allowed, form=None, change=False)
        self.assertTrue(allowed.include_in_parent_ecosystem)

        tampered = ResearchProject(
            unit=self.latec,
            axis=self.other_axis,
            title="Pesquisa adulterada pela mentora",
            slug="pesquisa-adulterada-pela-mentora",
        )
        with self.assertRaises(PermissionDenied):
            project_admin.save_model(request, tampered, form=None, change=False)


class FinalLegacyCutMigrationTests(TransactionTestCase):
    reset_sequences = True
    old_targets = [
        ("accounts", "0002_add_institutional_admin_scope"),
        ("axes", "0002_researchaxis_unit"),
        ("core", "0002_herobanner_unit_institutionalsection_unit_and_more"),
        ("institutional", "0002_validate_and_add_institutional_constraints"),
        ("learning", "0003_course_unit_event_unit_learningtrack_unit"),
        ("metrics", "0002_impactmetric_unit"),
        ("news", "0002_post_unit"),
        ("people", "0001_initial"),
        ("portfolio", "0002_project_unit"),
        ("research", "0002_convert_legacy_portfolio_categories"),
        ("scientific", "0003_scientificoutput_academic_work_and_more"),
        ("transparency", "0002_transparencydocument_unit"),
    ]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.latest_targets = self.executor.loader.graph.leaf_nodes()
        self.executor.migrate(self.old_targets)
        self.old_apps = self.executor.loader.project_state(self.old_targets).apps

    def tearDown(self):
        MigrationExecutor(connection).migrate(self.latest_targets)
        super().tearDown()

    def _create_valid_legacy_graph(self):
        Unit = self.old_apps.get_model("institutional", "InstitutionalUnit")
        Role = self.old_apps.get_model("people", "Role")
        Person = self.old_apps.get_model("people", "Person")
        Membership = self.old_apps.get_model("institutional", "InstitutionMembership")
        Category = self.old_apps.get_model("portfolio", "ProjectCategory")
        Project = self.old_apps.get_model("portfolio", "Project")
        Research = self.old_apps.get_model("research", "ResearchProject")
        ResearchMember = self.old_apps.get_model("research", "ResearchProjectMember")
        Scientific = self.old_apps.get_model("scientific", "ScientificOutput")
        Metric = self.old_apps.get_model("metrics", "ImpactMetric")
        unit = Unit.objects.create(name="LATEC", acronym="LATEC", slug="latec-cut", unit_type="academic_league")
        role = Role.objects.create(name="Pesquisador", slug="pesquisador-cut")
        person = Person.objects.create(full_name="Pessoa do corte", slug="pessoa-corte", role=role)
        Membership.objects.create(person=person, unit=unit, role="Pesquisador")
        category = Category.objects.create(name="Pesquisa", slug="pesquisa")
        source = Project.objects.create(
            unit=unit,
            category=category,
            title="Pesquisa legada",
            slug="pesquisa-legada-cut",
            editorial_status="published",
            is_published=True,
        )
        destination = Research.objects.create(
            unit=unit,
            legacy_portfolio_project_id=source.pk,
            title=source.title,
            slug=source.slug,
        )
        member = ResearchMember.objects.create(
            research_project=destination,
            person=person,
            role="researcher",
            is_coordinator=True,
        )
        legacy_type = Scientific.objects.create(
            unit=unit,
            title="Tipo científico legado",
            slug="tipo-cientifico-legado",
            output_type="project",
        )
        Metric.objects.create(unit=unit, key="eventos", label="Eventos", value=0)
        return source.pk, destination.pk, member.pk, legacy_type.pk

    def test_cut_publishes_destination_archives_source_and_removes_legacy_state(self):
        source_id, destination_id, member_id, legacy_type_id = self._create_valid_legacy_graph()
        MigrationExecutor(connection).migrate(self.latest_targets)

        from apps.metrics.models import ImpactMetric
        from apps.portfolio.models import Project, ProjectCategory
        from apps.research.models import ResearchProject, ResearchProjectMember
        from apps.scientific.models import ScientificOutput

        source = Project.objects.get(pk=source_id)
        destination = ResearchProject.objects.get(pk=destination_id)
        self.assertEqual(source.editorial_status, EditorialStatus.ARCHIVED)
        self.assertIsNone(source.category)
        self.assertEqual(destination.editorial_status, EditorialStatus.PUBLISHED)
        self.assertIsNotNone(destination.published_at)
        self.assertFalse(ProjectCategory.objects.filter(slug="pesquisa").exists())
        self.assertFalse(ImpactMetric.objects.filter(key="eventos").exists())
        self.assertFalse(hasattr(destination, "legacy_portfolio_project_id"))
        self.assertEqual(
            ResearchProjectMember.objects.get(pk=member_id).role,
            ResearchProjectMember.Role.COORDINATOR,
        )
        self.assertEqual(
            ScientificOutput.objects.get(pk=legacy_type_id).output_type,
            ScientificOutput.OutputType.OTHER,
        )

    def test_preflight_reports_all_destructive_blockers_before_writing(self):
        Unit = self.old_apps.get_model("institutional", "InstitutionalUnit")
        Role = self.old_apps.get_model("people", "Role")
        Person = self.old_apps.get_model("people", "Person")
        Category = self.old_apps.get_model("portfolio", "ProjectCategory")
        Project = self.old_apps.get_model("portfolio", "Project")
        Metric = self.old_apps.get_model("metrics", "ImpactMetric")
        Post = self.old_apps.get_model("news", "Post")
        Scientific = self.old_apps.get_model("scientific", "ScientificOutput")
        unit = Unit.objects.create(name="Unidade", acronym="U", slug="unidade-preflight", unit_type="initiative")
        role = Role.objects.create(name="Papel sem membership", slug="papel-sem-membership")
        person = Person.objects.create(full_name="Pessoa inconsistente", slug="pessoa-inconsistente", role=role)
        category = Category.objects.create(name="Produção científica", slug="producao-cientifica")
        source = Project.objects.create(
            unit=unit,
            category=category,
            title="Projeto sem destino",
            slug="projeto-sem-destino",
        )
        metric = Metric.objects.create(unit=unit, key="eventos", label="Eventos", value=1)
        post = Post.objects.create(
            unit=None,
            title="Publicação contraditória",
            slug="publicacao-contraditoria",
            content="texto",
            status="published",
            is_published=False,
        )
        output = Scientific.objects.create(
            unit=unit,
            title="Autores externos",
            slug="autores-externos",
            output_type="article",
            authors="Pessoa Externa",
        )
        migration = import_module("apps.research.migrations.0003_final_legacy_cut")

        with self.assertRaisesMessage(RuntimeError, f"news.Post com publicação contraditória: [{post.pk}]") as error:
            migration.preflight_and_cut(
                self.old_apps,
                SimpleNamespace(connection=connection),
            )
        message = str(error.exception)
        self.assertIn(f"news.Post sem unit: [{post.pk}]", message)
        self.assertIn(f"people.Person sem membership equivalente ao role legado: [{person.pk}]", message)
        self.assertIn(f"scientific.ScientificOutput com authors textual: [{output.pk}]", message)
        self.assertIn(f"portfolio.Project legado sem destino convertido: [{source.pk}]", message)
        self.assertTrue(Metric.objects.filter(pk=metric.pk).exists())
        self.assertEqual(Project.objects.get(pk=source.pk).category_id, category.pk)
        output.delete()
        post.delete()
        source.delete()
        category.delete()
        person.delete()
        role.delete()
        metric.delete()
