from datetime import date, datetime, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.accounts.models import Profile
from apps.common.models import EditorialStatus
from apps.core.models import SocialLink
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.learning.models import Course
from apps.metrics.models import ImpactMetric, MetricSnapshot
from apps.news.models import Post
from apps.partnerships.models import ContactMessage, Partner
from apps.people.models import Person
from apps.portfolio.models import Project
from apps.research.models import ResearchProject


class Command(BaseCommand):
    help = "Cria dados de borda idempotentes para desenvolvimento e homologação."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            help="Senha dos usuários administrativos de teste; sem ela, esses usuários não são criados.",
        )

    def handle(self, *args, **options):
        self.labtec = InstitutionalUnit.objects.filter(slug="labtec-in").first()
        self.latec = InstitutionalUnit.objects.filter(slug="latec").first()
        if not self.labtec or not self.latec:
            raise CommandError("Execute 'python manage.py seed_initial_data' antes deste comando.")

        self.seed_units()
        self.seed_people_and_memberships()
        self.seed_editorial_content()
        self.seed_support_data()
        if options.get("password"):
            self.seed_admin_users(options["password"])
        else:
            self.stdout.write("Usuários administrativos omitidos; use --password para incluí-los.")
        self.stdout.write(self.style.SUCCESS("Dados de borda concluídos."))

    def seed_units(self):
        self.nucleus = self.unit(
            "nucleo-latec-teste",
            "Núcleo LATEC (teste)",
            "NLT",
            InstitutionalUnit.UnitType.INITIATIVE,
            self.latec,
            90,
        )
        self.external_unit = self.unit(
            "unidade-externa-teste",
            "Unidade externa (teste)",
            "UET",
            InstitutionalUnit.UnitType.RESEARCH_GROUP,
            None,
            91,
        )

    def unit(self, slug, name, acronym, unit_type, parent, display_order):
        return InstitutionalUnit.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "acronym": acronym,
                "unit_type": unit_type,
                "parent": parent,
                "description": "Unidade criada para testar hierarquia e escopos.",
                "display_order": display_order,
            },
        )[0]

    def seed_people_and_memberships(self):
        self.people = {
            slug: Person.objects.update_or_create(
                slug=slug,
                defaults={
                    "full_name": name,
                    "short_bio": bio,
                    "is_active": True,
                    "display_order": 90,
                },
            )[0]
            for slug, name, bio in (
                ("pessoa-sem-vinculo-teste", "Pessoa sem vínculo (teste)", "Registro sem vínculo institucional."),
                ("pessoa-multiplos-vinculos-teste", "Pessoa com múltiplos vínculos (teste)", "Registro associado a mais de uma unidade."),
                ("pessoa-vinculo-inativo-teste", "Pessoa com vínculo inativo (teste)", "Registro com vínculo encerrado."),
                ("pessoa-vinculo-futuro-teste", "Pessoa com vínculo futuro (teste)", "Registro com vínculo ainda não iniciado."),
            )
        }

        memberships = (
            ("pessoa-multiplos-vinculos-teste", self.labtec, "Pesquisador", {}),
            ("pessoa-multiplos-vinculos-teste", self.latec, "Orientador", {}),
            ("pessoa-multiplos-vinculos-teste", self.external_unit, "Colaborador externo", {"is_active": False, "is_public": False, "end_date": date(2025, 12, 31)}),
            ("pessoa-vinculo-inativo-teste", self.latec, "Vínculo encerrado", {"is_active": False, "is_public": False, "start_date": date(2024, 1, 1), "end_date": date(2025, 12, 31)}),
            ("pessoa-vinculo-futuro-teste", self.latec, "Vínculo futuro", {"start_date": date(2099, 1, 1)}),
        )
        for person_slug, unit, role, extra in memberships:
            InstitutionMembership.objects.update_or_create(
                person=self.people[person_slug],
                unit=unit,
                role=role,
                defaults={"is_active": True, "is_public": True, "display_order": 90, **extra},
            )

    def seed_editorial_content(self):
        projects = (
            ("projeto-rascunho-teste", "Projeto em rascunho (teste)", self.latec, EditorialStatus.DRAFT, None, False),
            ("projeto-em-revisao-nucleo-teste", "Projeto em revisão no núcleo (teste)", self.nucleus, EditorialStatus.IN_REVIEW, None, True),
            ("projeto-arquivado-teste", "Projeto arquivado (teste)", self.external_unit, EditorialStatus.ARCHIVED, None, False),
        )
        for slug, title, unit, editorial_status, status, include_in_parent in projects:
            Project.objects.update_or_create(
                slug=slug,
                defaults={
                    "unit": unit,
                    "title": title,
                    "status": status,
                    "editorial_status": editorial_status,
                    "published_at": self.timestamp() if editorial_status == EditorialStatus.PUBLISHED else None,
                    "include_in_parent_ecosystem": include_in_parent,
                },
            )

        Post.objects.filter(slug="post-publicado-teste").delete()
        for slug, title, status in (
            ("post-rascunho-teste", "Post em rascunho (teste)", EditorialStatus.DRAFT),
            ("post-arquivado-teste", "Post arquivado (teste)", EditorialStatus.ARCHIVED),
        ):
            Post.objects.update_or_create(
                slug=slug,
                defaults={
                    "unit": self.latec,
                    "title": title,
                    "summary": "Registro editorial de borda.",
                    "content": "Conteúdo criado para testar o workflow editorial.",
                    "editorial_status": status,
                    "published_at": self.timestamp() if status == EditorialStatus.PUBLISHED else None,
                },
            )

        for slug, title, enrollment_status, editorial_status in (
            ("curso-rascunho-teste", "Curso em rascunho (teste)", Course.EnrollmentStatus.CLOSED, EditorialStatus.DRAFT),
            ("curso-concluido-teste", "Curso concluído (teste)", Course.EnrollmentStatus.COMPLETED, EditorialStatus.PUBLISHED),
        ):
            Course.objects.update_or_create(
                slug=slug,
                defaults={
                    "unit": self.latec,
                    "title": title,
                    "description": "Curso criado para testar status e campos opcionais.",
                    "start_date": date(2026, 7, 1),
                    "enrollment_status": enrollment_status,
                    "editorial_status": editorial_status,
                    "published_at": self.timestamp() if editorial_status == EditorialStatus.PUBLISHED else None,
                },
            )

        for slug, title, status in (
            ("pesquisa-publicada-teste", "Pesquisa publicada (teste)", EditorialStatus.PUBLISHED),
            ("pesquisa-suspensa-rascunho-teste", "Pesquisa suspensa em rascunho (teste)", EditorialStatus.DRAFT),
        ):
            ResearchProject.objects.update_or_create(
                slug=slug,
                defaults={
                    "unit": self.nucleus,
                    "title": title,
                    "summary": "Pesquisa criada para testar status e filtros públicos.",
                    "project_status": ResearchProject.ProjectStatus.SUSPENDED,
                    "editorial_status": status,
                    "published_at": self.timestamp() if status == EditorialStatus.PUBLISHED else None,
                },
            )

    def seed_support_data(self):
        partner = Partner.objects.update_or_create(
            slug="parceiro-multiplas-unidades-teste",
            defaults={
                "name": "Parceiro com múltiplas unidades (teste)",
                "partner_type": Partner.PartnerType.ACADEMIC,
                "description": "Parceiro associado a mais de uma unidade.",
                "is_active": True,
                "display_order": 90,
            },
        )[0]
        partner.units.set((self.labtec, self.latec))
        Partner.objects.update_or_create(
            slug="parceiro-inativo-teste",
            defaults={
                "name": "Parceiro inativo (teste)",
                "partner_type": Partner.PartnerType.OTHER,
                "description": "Registro que não deve aparecer publicamente.",
                "is_active": False,
                "display_order": 91,
            },
        )

        for subject, status in (
            ("Mensagem nova (teste)", ContactMessage.MessageStatus.NEW),
            ("Mensagem em atendimento (teste)", ContactMessage.MessageStatus.IN_PROGRESS),
            ("Mensagem respondida (teste)", ContactMessage.MessageStatus.ANSWERED),
            ("Mensagem arquivada (teste)", ContactMessage.MessageStatus.ARCHIVED),
        ):
            ContactMessage.objects.update_or_create(
                subject=subject,
                email="teste-edge@example.com",
                defaults={
                    "contact_type": ContactMessage.ContactType.OTHER,
                    "name": "Contato de teste",
                    "organization": "LABTEC.IN",
                    "message": "Mensagem criada para testar o fluxo de atendimento.",
                    "status": status,
                },
            )

        SocialLink.objects.update_or_create(
            label="Link social ativo (teste)",
            defaults={"unit": self.labtec, "url": "https://example.com/social-edge", "icon": "globe", "is_active": True, "display_order": 90},
        )
        SocialLink.objects.update_or_create(
            label="Link social inativo (teste)",
            defaults={"unit": self.latec, "url": "https://example.com/social-edge-inactive", "icon": "globe", "is_active": False, "display_order": 91},
        )

        metric = ImpactMetric.objects.filter(unit=self.labtec).order_by("display_order").first()
        if metric:
            for reference_date, value in ((date(2025, 12, 31), 0), (date(2026, 6, 30), metric.value)):
                MetricSnapshot.objects.update_or_create(
                    metric=metric,
                    reference_date=reference_date,
                    defaults={"value": value, "note": "Snapshot de borda para testes temporais."},
                )

    def seed_admin_users(self, password):
        User = get_user_model()
        specs = (
            ("edge-lab-coordinator", Profile.AdminRole.LAB_COORDINATOR, self.labtec, self.people["pessoa-multiplos-vinculos-teste"], True, (self.labtec,)),
            ("edge-unit-coordinator", Profile.AdminRole.UNIT_COORDINATOR, self.latec, None, False, (self.latec,)),
            ("edge-inactive-admin", Profile.AdminRole.UNIT_COORDINATOR, self.latec, None, False, (self.latec,)),
            ("edge-wrong-lab-coordinator", Profile.AdminRole.LAB_COORDINATOR, self.latec, None, False, (self.latec,)),
        )
        for username, role, unit, person, inherit, authorized_units in specs:
            user = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})[0]
            user.email = f"{username}@example.com"
            user.first_name = username.replace("-", " ").title()
            user.is_staff = True
            user.is_active = username != "edge-inactive-admin"
            user.set_password(password)
            user.save(update_fields=("email", "first_name", "is_staff", "is_active", "password"))
            profile = Profile.objects.get_or_create(user=user, defaults={"role": role})[0]
            profile.role = role
            profile.primary_unit = unit
            profile.person = person
            profile.inherit_descendants = inherit
            profile.is_active_admin = username != "edge-inactive-admin"
            profile.save()
            profile.authorized_units.set(authorized_units)

        user = User.objects.get_or_create(username="edge-no-profile", defaults={"email": "edge-no-profile@example.com"})[0]
        user.email = "edge-no-profile@example.com"
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=("email", "is_staff", "is_active", "password"))

    def timestamp(self):
        return timezone.make_aware(datetime.combine(date(2026, 7, 1), time.min))
