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
            InstitutionalUnit: {"nucleo-latec-teste", "unidade-externa-teste"},
            Person: {
                "pessoa-sem-vinculo-teste",
                "pessoa-multiplos-vinculos-teste",
                "pessoa-vinculo-inativo-teste",
                "pessoa-vinculo-futuro-teste",
            },
            Project: {
                "projeto-rascunho-teste",
                "projeto-em-revisao-nucleo-teste",
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
            3,
        )
        self.assertEqual(get_user_model().objects.filter(username__startswith="edge-").count(), 6)
        self.assertEqual(Profile.objects.filter(user__username__startswith="edge-").count(), 5)

    def test_edge_hierarchy_and_membership_visibility_are_present(self):
        nucleus = InstitutionalUnit.objects.get(slug="nucleo-latec-teste")
        self.assertEqual(nucleus.parent.slug, "latec")

        inactive = InstitutionMembership.objects.get(role="Vínculo encerrado")
        self.assertFalse(inactive.is_active)
        self.assertFalse(inactive.is_public)

        future = InstitutionMembership.objects.get(role="Vínculo futuro")
        self.assertEqual(future.start_date.year, 2099)

    def test_editorial_edge_data_only_published_records_are_public(self):
        for endpoint, hidden_slugs in {
            "projects": {
                "projeto-rascunho-teste",
                "projeto-em-revisao-nucleo-teste",
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
