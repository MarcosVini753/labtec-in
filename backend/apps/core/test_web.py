from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from apps.accounts.models import Profile
from apps.common.models import EditorialStatus
from apps.institutional.models import InstitutionalUnit
from apps.portfolio.models import Project
from apps.partnerships.models import ContactMessage
from apps.people.models import Person


class PortalWebTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_initial_data", verbosity=0)

    def test_public_pages_and_startup_detail_are_database_backed(self):
        for path in (
            "/",
            "/unidades/latec/",
            "/sobre/",
            "/portfolio/",
            "/portfolio/projetos/startups/",
            "/portfolio/projetos/farma-amazonia/",
            "/portfolio/pesquisas/",
            "/portfolio/tccs/",
            "/portfolio/producao-cientifica/",
            "/portfolio/transparencia/",
            "/noticias/",
            "/capacitacao/",
            "/parceiros/",
            "/contato/",
            "/busca/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        home = self.client.get("/")
        self.assertContains(home, "people/marta.png")
        self.assertContains(home, "Equipe")
        self.assertNotContains(home, ">Todos<")
        self.assertNotContains(home, ">Ligantes<")
        self.assertContains(self.client.get("/portfolio/projetos/farma-amazonia/"), "Astrocaryum ulei")

    def test_startup_detail_renders_compact_profile_and_empty_field(self):
        response = self.client.get("/portfolio/projetos/remedio-vivo/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="startup-profile"')
        self.assertContains(response, 'class="startup-profile-item"', count=3)
        self.assertContains(response, "Área/foco")
        self.assertContains(response, "Microverdes &amp; Nutracêuticos")
        self.assertContains(response, "Espécie/objeto")
        self.assertContains(response, 'class="is-empty">Não informado</dd>')
        self.assertContains(response, "Instituição")
        self.assertContains(response, "UFAC/LABTEC.IN")

    def test_home_highlights_published_content_from_the_ecosystem(self):
        home = self.client.get("/")
        latec = self.client.get("/unidades/latec/")
        self.assertContains(home, "Farma Amazônia")
        self.assertContains(home, "Coordenadora da LABTEC.IN é premiada por inovação tecnológica")
        self.assertNotContains(home, 'data-profile-role="ligante"')
        self.assertNotContains(home, '<span class="tag">Ligante</span>')
        self.assertContains(latec, "Farma Amazônia")
        self.assertContains(latec, "Ligante")

    def test_award_news_renders_seeded_images_and_labeled_external_link(self):
        marta = self.client.get("/noticias/coordenadora-da-latec-e-premiada-por-inovacao-tecnologica/")
        bruna = self.client.get("/noticias/professora-do-labtec-in-e-homenageada-por-trajetoria-na-nutricao/")

        self.assertEqual(marta.status_code, 200)
        self.assertContains(marta, "Coordenadora da LABTEC.IN é premiada por inovação tecnológica")
        self.assertContains(marta, "premioMarta.png")
        self.assertContains(marta, "certificado.png")
        self.assertContains(
            marta,
            'href="https://cbae.ufrj.br/2026/05/25/5-congresso-brasileiro-de-educacao-empreendedora-sustentabilidade-e-inovacao/"',
        )
        self.assertContains(
            marta,
            ">5ª edição dos Congressos Brasileiro e Internacional de Educação Empreendedora, Sustentabilidade e Inovação</a>",
        )
        self.assertEqual(bruna.status_code, 200)
        self.assertContains(bruna, "Professora do LABTEC.IN recebe o título de Dama Comendadora por trajetória acadêmica em nutrição")
        self.assertContains(bruna, "premioBruna.png")

    def test_gabriel_news_is_public_and_uses_labeled_links(self):
        response = self.client.get("/noticias/estagiario-do-labtec-in-participara-de-forum-sobre-internet-no-quenia/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estagiário do LABTEC.IN participará de fórum sobre internet no Quênia")
        self.assertContains(response, "gabriel.png")
        self.assertContains(response, 'href="https://intgovforum.org/en/dashboard/igf-2026"')
        self.assertContains(response, ">21ª reunião anual do Fórum de Governança da Internet</a>")

    def test_global_search_filters_unpublished_content_and_unit(self):
        Project.objects.create(
            unit=InstitutionalUnit.objects.get(slug="latec"),
            title="Rascunho secreto",
            slug="rascunho-secreto",
            editorial_status=EditorialStatus.DRAFT,
        )
        response = self.client.get("/api/v1/search/?q=farma&type=project&unit=latec")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(item["slug"] != "rascunho-secreto" for item in response.json()["results"]))
        self.assertTrue(any(item["slug"] == "farma-amazonia" for item in response.json()["results"]))

    def test_contact_api_returns_htmx_feedback_and_persists_message(self):
        response = self.client.post(
            "/api/v1/contact/",
            {
                "contact_type": "partnership",
                "subject": "Parceria",
                "name": "Pessoa de teste",
                "email": "teste@example.com",
                "message": "Gostaria de conversar.",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 201)
        self.assertContains(response, "Mensagem enviada", status_code=201)
        self.assertEqual(ContactMessage.objects.get().status, ContactMessage.MessageStatus.NEW)

    def test_contact_page_posts_without_javascript_and_preserves_invalid_data(self):
        payload = {
            "contact_type": "questions",
            "subject": "Informações",
            "name": "Visitante",
            "email": "visitante@example.com",
            "message": "Gostaria de saber mais.",
        }
        response = self.client.post("/contato/", payload, follow=True)
        self.assertRedirects(response, "/contato/")
        self.assertContains(response, "Mensagem enviada com sucesso")
        self.assertEqual(ContactMessage.objects.filter(email=payload["email"]).count(), 1)

        invalid = {**payload, "subject": "Assunto preservado", "email": ""}
        response = self.client.post("/contato/", invalid)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Revise os campos", status_code=400)
        self.assertContains(response, 'value="Assunto preservado"', status_code=400)
        self.assertEqual(ContactMessage.objects.filter(subject="Assunto preservado").count(), 0)

    def test_contact_page_returns_htmx_feedback_for_success_and_validation(self):
        payload = {
            "contact_type": "press",
            "subject": "Imprensa",
            "name": "Assessoria",
            "email": "assessoria@example.com",
            "message": "Solicitação de entrevista.",
        }
        response = self.client.post("/contato/", payload, HTTP_HX_REQUEST="true")
        self.assertContains(response, "Mensagem enviada", status_code=201)
        self.assertEqual(ContactMessage.objects.filter(email=payload["email"]).count(), 1)

        response = self.client.post("/contato/", {**payload, "contact_type": "invalid"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revise os campos")
        self.assertEqual(ContactMessage.objects.filter(email=payload["email"]).count(), 1)

    def test_authenticated_contact_post_accepts_a_real_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(get_user_model().objects.create_superuser("csrf-admin", password="password"))
        client.get("/contato/")
        token = client.cookies["csrftoken"].value
        response = client.post(
            "/contato/",
            {
                "csrfmiddlewaretoken": token,
                "contact_type": "other",
                "subject": "Sessão autenticada",
                "name": "Administradora",
                "email": "admin@example.com",
                "message": "Teste com CSRF.",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ContactMessage.objects.filter(subject="Sessão autenticada").exists())

    def test_only_active_administrative_scope_can_use_portal_login(self):
        user = get_user_model().objects.create_user(username="sem-escopo", password="senha", is_staff=True)
        denied = self.client.post("/entrar/", {"username": user.username, "password": "senha"})
        self.assertContains(denied, "não possui um perfil administrativo ativo e válido")
        self.assertNotIn("_auth_user_id", self.client.session)

        incomplete = get_user_model().objects.create_user(
            username="perfil-sem-unidade",
            password="senha",
            is_staff=True,
        )
        Profile.objects.create(user=incomplete, role=Profile.AdminRole.UNIT_COORDINATOR)
        denied = self.client.post("/entrar/", {"username": incomplete.username, "password": "senha"})
        self.assertContains(denied, "não possui um perfil administrativo ativo e válido")
        self.assertNotIn("_auth_user_id", self.client.session)

        self.client.force_login(user)
        response = self.client.get("/admin/")
        self.assertRedirects(response, "/entrar/?reason=admin-scope", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(response.url), "não possui um perfil administrativo ativo e válido")

        scoped = get_user_model().objects.create_user(username="coordenador", password="senha", is_staff=True)
        profile = Profile.objects.create(
            user=scoped,
            role=Profile.AdminRole.LAB_COORDINATOR,
            primary_unit=InstitutionalUnit.objects.get(slug="labtec-in"),
        )
        response = self.client.post("/entrar/", {"username": scoped.username, "password": "senha"})
        self.assertRedirects(response, "/admin/dashboard/")
        self.assertEqual(self.client.get("/admin/dashboard/").status_code, 200)
        partial = self.client.get("/admin/dashboard/?unit=latec", HTTP_HX_REQUEST="true")
        self.assertEqual(partial.status_code, 200)
        self.assertContains(partial, "published")

        latec = InstitutionalUnit.objects.get(slug="latec")
        mentor_person = Person.objects.create(full_name="Orientadora do login", slug="orientadora-login")
        for username, role, extra in (
            ("coordenador-unidade", Profile.AdminRole.UNIT_COORDINATOR, {}),
            ("orientador", Profile.AdminRole.MENTOR, {"person": mentor_person}),
        ):
            self.client.logout()
            account = get_user_model().objects.create_user(username=username, password="senha", is_staff=True)
            Profile.objects.create(user=account, role=role, primary_unit=latec, **extra)
            self.assertRedirects(
                self.client.post("/entrar/", {"username": username, "password": "senha"}),
                "/admin/dashboard/",
            )
