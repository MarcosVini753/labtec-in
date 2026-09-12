from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import Profile
from apps.common.models import EditorialStatus
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.learning.models import Course
from apps.news.models import Post
from apps.people.models import Person
from apps.portfolio.models import Project
from apps.research.models import ResearchProject


class EdgeCaseSeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_initial_data", verbosity=0)
        call_command("seed_edge_case_data", password="edge-test-password", verbosity=0)

    def test_seed_is_idempotent(self):
        call_command("seed_edge_case_data", password="edge-test-password", verbosity=0)

        expected_slugs = {
            Person: {
                "pessoa-sem-vinculo-teste",
                "pessoa-multiplos-vinculos-teste",
                "pessoa-vinculo-inativo-teste",
                "pessoa-vinculo-futuro-teste",
            },
            Project: {
                "projeto-rascunho-teste",
                "projeto-em-revisao-teste",
                "projeto-arquivado-teste",
            },
            Post: {"post-rascunho-teste", "post-arquivado-teste"},
            Course: {
                "curso-rascunho-teste",
                "curso-concluido-teste",
            },
            ResearchProject: {"pesquisa-publicada-teste", "pesquisa-suspensa-rascunho-teste"},
        }
        for model, slugs in expected_slugs.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(
                    set(model.objects.filter(slug__in=slugs).values_list("slug", flat=True)),
                    slugs,
                )

        self.assertEqual(
            InstitutionMembership.objects.filter(person__slug="pessoa-multiplos-vinculos-teste").count(),
            2,
        )
        self.assertEqual(get_user_model().objects.filter(username__startswith="edge-").count(), 5)
        self.assertEqual(Profile.objects.filter(user__username__startswith="edge-").count(), 4)

    def test_edge_membership_visibility_and_retired_units_are_handled(self):
        self.assertFalse(
            InstitutionalUnit.objects.filter(slug__in=("nucleo-latec-teste", "unidade-externa-teste")).exists()
        )
        self.assertFalse(Project.objects.filter(slug="projeto-em-revisao-nucleo-teste").exists())

        inactive = InstitutionMembership.objects.get(role="Vínculo encerrado")
        self.assertFalse(inactive.is_active)
        self.assertFalse(inactive.is_public)

        future = InstitutionMembership.objects.get(role="Vínculo futuro")
        self.assertEqual(future.start_date.year, 2099)

    def test_editorial_edge_data_only_published_records_are_public(self):
        for endpoint, hidden_slugs in {
            "projects": {
                "projeto-rascunho-teste",
                "projeto-em-revisao-teste",
                "projeto-arquivado-teste",
            },
            "posts": {"post-rascunho-teste", "post-arquivado-teste"},
            "courses": {"curso-rascunho-teste"},
            "research-projects": {"pesquisa-suspensa-rascunho-teste"},
        }.items():
            response = self.client.get(f"/api/v1/{endpoint}/")
            self.assertEqual(response.status_code, 200)
            visible_slugs = {item["slug"] for item in response.json()["results"]}
            self.assertTrue(hidden_slugs.isdisjoint(visible_slugs))

    def test_seed_removes_the_retired_published_post_card(self):
        Post.objects.create(
            unit=InstitutionalUnit.objects.get(slug="latec"),
            title="Post publicado (teste)",
            slug="post-publicado-teste",
            content="Registro editorial de borda.",
            editorial_status=EditorialStatus.PUBLISHED,
        )

        call_command("seed_edge_case_data", password="edge-test-password", verbosity=0)

        self.assertFalse(Post.objects.filter(slug="post-publicado-teste").exists())

    def test_seed_retires_removed_test_units_and_their_content(self):
        latec = InstitutionalUnit.objects.get(slug="latec")
        nucleus = InstitutionalUnit.objects.create(
            name="Núcleo LATEC (teste)",
            acronym="NLT",
            slug="nucleo-latec-teste",
            unit_type=InstitutionalUnit.UnitType.INITIATIVE,
            parent=latec,
        )
        external = InstitutionalUnit.objects.create(
            name="Unidade externa (teste)",
            acronym="UET",
            slug="unidade-externa-teste",
            unit_type=InstitutionalUnit.UnitType.RESEARCH_GROUP,
        )
        Project.objects.create(
            unit=nucleus,
            title="Projeto em revisão no núcleo (teste)",
            slug="projeto-em-revisao-nucleo-teste",
            editorial_status=EditorialStatus.IN_REVIEW,
        )
        person = Person.objects.get(slug="pessoa-multiplos-vinculos-teste")
        InstitutionMembership.objects.create(
            person=person,
            unit=external,
            role="Colaborador externo",
            is_active=False,
            is_public=False,
        )

        call_command("seed_edge_case_data", password="edge-test-password", verbosity=0)

        self.assertFalse(
            InstitutionalUnit.objects.filter(slug__in=("nucleo-latec-teste", "unidade-externa-teste")).exists()
        )
        self.assertFalse(Project.objects.filter(slug="projeto-em-revisao-nucleo-teste").exists())
        self.assertFalse(InstitutionMembership.objects.filter(role="Colaborador externo").exists())
        self.assertTrue(Project.objects.filter(slug="projeto-em-revisao-teste").exists())

    def test_admin_edge_users_have_expected_scope(self):
        User = get_user_model()
        lab_user = User.objects.get(username="edge-lab-coordinator")
        mentor_user = User.objects.get(username="edge-mentor")
        inactive_user = User.objects.get(username="edge-inactive-admin")

        self.assertTrue(lab_user.check_password("edge-test-password"))
        self.assertEqual(lab_user.profile.role, Profile.AdminRole.LAB_COORDINATOR)
        self.assertEqual(mentor_user.profile.role, Profile.AdminRole.MENTOR)
        self.assertTrue(mentor_user.profile.mentor_axis_ids())
        self.assertFalse(inactive_user.is_active)
        self.assertFalse(inactive_user.profile.is_active_admin)
