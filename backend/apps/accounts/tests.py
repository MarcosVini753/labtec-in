import importlib
from types import SimpleNamespace

from django.apps import apps as django_apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.forms import inlineformset_factory, modelform_factory
from django.test import RequestFactory, TestCase

from apps.accounts.admin import (
    ProfileAdmin,
    ProfileAdminForm,
    RequiredStaffProfileFormSet,
    ScopedUserAdmin,
)
from apps.accounts.models import Profile
from apps.axes.models import AxisMentorship, ResearchAxis
from apps.common.admin_actions import mark_as_archived, mark_as_in_review, mark_as_published
from apps.common.models import EditorialStatus
from apps.institutional.admin import InstitutionMembershipAdmin, InstitutionalUnitAdmin
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.partnerships.admin import ContactMessageAdmin, PartnerAdmin
from apps.partnerships.models import ContactMessage, Partner
from apps.people.models import Person
from apps.portfolio.admin import ProjectAdmin, ProjectTeamMemberAdmin, ProjectTeamMemberInline
from apps.portfolio.models import Project, ProjectStatus, ProjectTeamMember


class InstitutionalAdminPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.labtec = InstitutionalUnit.objects.create(
            name="LABTEC.IN",
            acronym="LABTEC.IN",
            slug="labtec-in",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )
        cls.latec = InstitutionalUnit.objects.create(
            name="LATEC",
            acronym="LATEC",
            slug="latec",
            unit_type=InstitutionalUnit.UnitType.ACADEMIC_LEAGUE,
            parent=cls.labtec,
        )
        cls.descendant = InstitutionalUnit.objects.create(
            name="Núcleo LATEC",
            acronym="NL",
            slug="nucleo-latec",
            unit_type=InstitutionalUnit.UnitType.INITIATIVE,
            parent=cls.latec,
        )
        cls.other = InstitutionalUnit.objects.create(
            name="Outro laboratório",
            acronym="OUTRO",
            slug="outro",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )

        cls.mentor_person = Person.objects.create(full_name="Mentora", slug="mentora")
        cls.member = Person.objects.create(full_name="Integrante", slug="integrante")
        InstitutionMembership.objects.create(person=cls.mentor_person, unit=cls.latec, role="Orientador")
        InstitutionMembership.objects.create(person=cls.member, unit=cls.latec, role="Integrante")
        cls.mentor_axis = ResearchAxis.objects.create(
            unit=cls.latec,
            number=1,
            title="Eixo mentorado",
            slug="eixo-mentorado",
        )
        cls.other_axis = ResearchAxis.objects.create(
            unit=cls.latec,
            number=2,
            title="Outro eixo",
            slug="outro-eixo",
        )
        AxisMentorship.objects.create(axis=cls.mentor_axis, person=cls.mentor_person)

        cls.projects = {
            "labtec": Project.objects.create(unit=cls.labtec, title="Projeto LABTEC", slug="projeto-labtec"),
            "latec": Project.objects.create(
                unit=cls.latec,
                axis=cls.mentor_axis,
                title="Projeto LATEC",
                slug="projeto-latec",
            ),
            "latec_other": Project.objects.create(
                unit=cls.latec,
                axis=cls.other_axis,
                title="Projeto em outro eixo",
                slug="projeto-outro-eixo",
            ),
            "descendant": Project.objects.create(
                unit=cls.descendant,
                title="Projeto descendente",
                slug="projeto-descendente",
            ),
            "other": Project.objects.create(unit=cls.other, title="Projeto externo", slug="projeto-externo"),
        }

        cls.users = {
            "superuser": get_user_model().objects.create_superuser("superuser", "super@example.com", "password"),
            "no_profile": get_user_model().objects.create_user("no_profile", is_staff=True),
        }
        cls.profiles = {}
        cls._make_profile(
            "lab_coordinator",
            Profile.AdminRole.LAB_COORDINATOR,
            primary_unit=cls.labtec,
            inherit_descendants=True,
        )
        cls._make_profile("unit_coordinator", Profile.AdminRole.UNIT_COORDINATOR, primary_unit=cls.latec)
        cls._make_profile(
            "mentor",
            Profile.AdminRole.MENTOR,
            primary_unit=cls.latec,
            person=cls.mentor_person,
        )
        cls._make_profile(
            "inactive",
            Profile.AdminRole.UNIT_COORDINATOR,
            primary_unit=cls.latec,
            is_active_admin=False,
        )
        cls._make_profile(
            "wrong_lab",
            Profile.AdminRole.LAB_COORDINATOR,
            primary_unit=cls.latec,
        )

    @classmethod
    def _make_profile(cls, username, role, **kwargs):
        user = get_user_model().objects.create_user(username, is_staff=True)
        profile = Profile.objects.create(user=user, role=role, **kwargs)
        cls.users[username] = user
        cls.profiles[username] = profile

    def setUp(self):
        self.factory = RequestFactory()
        self.project_admin = ProjectAdmin(Project, admin.site)

    def request_for(self, username, method="get"):
        request = getattr(self.factory, method)("/admin/")
        request.user = self.users[username]
        return request

    def project_slugs_for(self, username):
        return set(
            self.project_admin.get_queryset(self.request_for(username)).values_list("slug", flat=True)
        )

    def test_queryset_matrix_and_descendant_inheritance(self):
        self.assertEqual(self.project_slugs_for("superuser"), {p.slug for p in self.projects.values()})
        self.assertEqual(
            self.project_slugs_for("lab_coordinator"),
            {"projeto-labtec", "projeto-latec", "projeto-outro-eixo", "projeto-descendente"},
        )
        self.assertEqual(
            self.project_slugs_for("unit_coordinator"),
            {"projeto-latec", "projeto-outro-eixo"},
        )
        self.profiles["unit_coordinator"].inherit_descendants = True
        self.profiles["unit_coordinator"].save(update_fields=("inherit_descendants",))
        self.assertIn("projeto-descendente", self.project_slugs_for("unit_coordinator"))
        self.assertEqual(self.project_slugs_for("mentor"), {"projeto-latec"})
        self.assertFalse(self.project_slugs_for("inactive"))
        self.assertFalse(self.project_slugs_for("no_profile"))
        self.assertFalse(self.project_slugs_for("wrong_lab"))

    def test_only_superuser_and_lab_coordinator_publish_or_edit_final_content(self):
        project = self.projects["latec"]
        project.editorial_status = EditorialStatus.PUBLISHED
        project.save(update_fields=("editorial_status",))

        for username in ("unit_coordinator", "mentor", "wrong_lab"):
            request = self.request_for(username)
            self.assertFalse(self.project_admin.has_change_permission(request, project))
            self.assertFalse(self.project_admin.has_delete_permission(request, project))
            self.assertNotIn("mark_as_published", self.project_admin.get_actions(request))
            self.assertNotIn("mark_as_archived", self.project_admin.get_actions(request))

        for username in ("superuser", "lab_coordinator"):
            request = self.request_for(username)
            self.assertTrue(self.project_admin.has_change_permission(request, project))
            self.assertTrue(self.project_admin.has_delete_permission(request, project))
            self.assertIn("mark_as_published", self.project_admin.get_actions(request))
            self.assertIn("mark_as_archived", self.project_admin.get_actions(request))

        draft = self.projects["latec_other"]
        mark_as_published(
            self.project_admin,
            self.request_for("unit_coordinator", method="post"),
            Project.objects.filter(pk=draft.pk),
        )
        draft.refresh_from_db()
        self.assertEqual(draft.editorial_status, EditorialStatus.DRAFT)
        mark_as_published(
            self.project_admin,
            self.request_for("lab_coordinator", method="post"),
            Project.objects.filter(pk=draft.pk),
        )
        draft.refresh_from_db()
        self.assertEqual(draft.editorial_status, EditorialStatus.PUBLISHED)
        self.assertIsNotNone(draft.published_at)

        review = Project.objects.create(
            unit=self.latec,
            title="Projeto em revisão",
            slug="projeto-em-revisao",
            status=ProjectStatus.objects.create(name="Em execução", slug="em-execucao"),
        )
        unit_request = self.request_for("unit_coordinator", method="post")
        mark_as_in_review(self.project_admin, unit_request, Project.objects.filter(pk=review.pk))
        review.refresh_from_db()
        self.assertEqual(review.editorial_status, EditorialStatus.IN_REVIEW)
        self.assertEqual(review.status.slug, "em-execucao")
        mark_as_archived(self.project_admin, unit_request, Project.objects.filter(pk=review.pk))
        review.refresh_from_db()
        self.assertEqual(review.editorial_status, EditorialStatus.IN_REVIEW)
        mark_as_archived(
            self.project_admin,
            self.request_for("lab_coordinator", method="post"),
            Project.objects.filter(pk=review.pk),
        )
        review.refresh_from_db()
        self.assertEqual(review.editorial_status, EditorialStatus.ARCHIVED)

    def test_server_side_save_rejects_tampered_scope_and_final_status(self):
        request = self.request_for("unit_coordinator", method="post")
        allowed = Project(
            unit=self.latec,
            title="Rascunho permitido",
            slug="rascunho-permitido",
            include_in_parent_ecosystem=True,
        )
        self.project_admin.save_model(request, allowed, form=None, change=False)
        self.assertTrue(allowed.include_in_parent_ecosystem)

        outside = Project(unit=self.other, title="Adulterado", slug="adulterado")
        with self.assertRaises(PermissionDenied):
            self.project_admin.save_model(request, outside, form=None, change=False)

        without_unit = Project(title="Sem unidade", slug="sem-unidade-adulterado")
        with self.assertRaises(PermissionDenied):
            self.project_admin.save_model(
                self.request_for("lab_coordinator", method="post"),
                without_unit,
                form=None,
                change=False,
            )

        final = Project(
            unit=self.latec,
            title="Publicação adulterada",
            slug="publicacao-adulterada",
            editorial_status=EditorialStatus.PUBLISHED,
        )
        with self.assertRaises(PermissionDenied):
            self.project_admin.save_model(request, final, form=None, change=False)

    def test_scoped_form_choices_and_children_cannot_bypass_a_published_parent(self):
        unit_request = self.request_for("unit_coordinator", method="post")
        unit_field = self.project_admin.formfield_for_foreignkey(
            Project._meta.get_field("unit"),
            unit_request,
        )
        self.assertEqual(set(unit_field.queryset), {self.latec})

        mentor_request = self.request_for("mentor", method="post")
        axis_field = self.project_admin.formfield_for_foreignkey(
            Project._meta.get_field("axis"),
            mentor_request,
        )
        self.assertEqual(set(axis_field.queryset), {self.mentor_axis})

        published = self.projects["latec"]
        published.editorial_status = EditorialStatus.PUBLISHED
        published.save(update_fields=("editorial_status",))
        inline = ProjectTeamMemberInline(Project, admin.site)
        self.assertFalse(inline.has_add_permission(unit_request, published))

        child = ProjectTeamMember(project=published, person=self.member)
        child_admin = ProjectTeamMemberAdmin(ProjectTeamMember, admin.site)
        with self.assertRaises(PermissionDenied):
            child_admin.save_model(unit_request, child, form=None, change=False)

    def test_sensitive_admin_models_and_shared_partners_remain_restricted(self):
        super_request = self.request_for("superuser")
        lab_request = self.request_for("lab_coordinator")
        unit_request = self.request_for("unit_coordinator")
        self.assertTrue(ProfileAdmin(Profile, admin.site).has_module_permission(super_request))
        self.assertFalse(ProfileAdmin(Profile, admin.site).has_module_permission(lab_request))
        self.assertTrue(InstitutionalUnitAdmin(InstitutionalUnit, admin.site).has_module_permission(super_request))
        self.assertFalse(InstitutionalUnitAdmin(InstitutionalUnit, admin.site).has_module_permission(lab_request))
        self.assertTrue(InstitutionMembershipAdmin(InstitutionMembership, admin.site).has_module_permission(lab_request))
        self.assertFalse(InstitutionMembershipAdmin(InstitutionMembership, admin.site).has_module_permission(unit_request))
        self.assertTrue(ContactMessageAdmin(ContactMessage, admin.site).has_module_permission(lab_request))
        contact_admin = ContactMessageAdmin(ContactMessage, admin.site)
        mentor_request = self.request_for("mentor")
        self.assertTrue(contact_admin.has_module_permission(unit_request))
        self.assertFalse(contact_admin.has_module_permission(mentor_request))

        contact = ContactMessage.objects.create(
            contact_type=ContactMessage.ContactType.QUESTIONS,
            subject="Atendimento compartilhado",
            name="Visitante",
            email="visitante@example.com",
            message="Preciso de informações.",
        )
        self.assertEqual(list(contact_admin.get_queryset(unit_request)), [contact])
        self.assertTrue(contact_admin.has_change_permission(unit_request, contact))
        self.assertFalse(contact_admin.has_add_permission(unit_request))
        self.assertFalse(contact_admin.has_delete_permission(unit_request, contact))
        self.assertEqual(
            set(contact_admin.get_readonly_fields(unit_request, contact)),
            {"contact_type", "subject", "message", "name", "email", "organization", "created_at", "updated_at"},
        )
        contact_form_class = contact_admin.get_form(unit_request, contact)
        self.assertEqual(set(contact_form_class.base_fields), {"status", "responded_at"})
        contact_form = contact_form_class(
            data={"status": ContactMessage.MessageStatus.IN_PROGRESS, "responded_at": ""},
            instance=contact,
        )
        self.assertTrue(contact_form.is_valid(), contact_form.errors)
        contact_admin.save_model(unit_request, contact_form.save(commit=False), contact_form, change=True)
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactMessage.MessageStatus.IN_PROGRESS)

        partner = Partner.objects.create(name="Parceiro compartilhado", slug="parceiro-compartilhado")
        partner.units.add(self.labtec, self.latec)
        partner_admin = PartnerAdmin(Partner, admin.site)
        self.assertFalse(partner_admin.has_change_permission(unit_request, partner))
        self.assertTrue(partner_admin.has_change_permission(lab_request, partner))
        tampered_form = SimpleNamespace(instance=partner, save_m2m=lambda: None)
        with self.assertRaises(PermissionDenied):
            partner_admin.save_related(unit_request, tampered_form, (), change=True)

    def test_new_profile_form_requires_an_explicit_supported_role(self):
        form_class = modelform_factory(Profile, fields=("role",))
        self.assertFalse(form_class(data={}).is_valid())
        self.assertEqual(
            {value for value, _label in Profile.AdminRole.choices},
            {"lab_coordinator", "unit_coordinator", "mentor"},
        )

    def test_active_profile_form_requires_a_valid_role_scope(self):
        user = get_user_model().objects.create_user("profile_form")
        common = {
            "user": user.pk,
            "role": Profile.AdminRole.LAB_COORDINATOR,
            "primary_unit": self.latec.pk,
            "authorized_units": [],
            "inherit_descendants": False,
            "is_active_admin": True,
        }
        form = ProfileAdminForm(data=common)
        self.assertFalse(form.is_valid())
        self.assertIn("LABTEC.IN", form.errors["primary_unit"][0])

        common.update(role=Profile.AdminRole.UNIT_COORDINATOR, primary_unit="")
        form = ProfileAdminForm(data=common)
        self.assertFalse(form.is_valid())
        self.assertIn("unidade", form.errors["primary_unit"][0])

        common.update(role=Profile.AdminRole.MENTOR, primary_unit=self.latec.pk, person="")
        form = ProfileAdminForm(data=common)
        self.assertFalse(form.is_valid())
        self.assertIn("pessoa", form.errors["person"][0])

    def test_staff_user_inline_requires_an_active_valid_profile(self):
        self.assertIn(Profile, [inline.model for inline in ScopedUserAdmin.inlines])
        formset_class = inlineformset_factory(
            get_user_model(),
            Profile,
            form=ProfileAdminForm,
            formset=RequiredStaffProfileFormSet,
            fields=(
                "person",
                "role",
                "primary_unit",
                "authorized_units",
                "inherit_descendants",
                "is_active_admin",
            ),
            extra=1,
            can_delete=True,
        )
        staff_user = get_user_model().objects.create_user("pending_staff", is_staff=True)
        self.client.force_login(self.users["superuser"])
        self.assertContains(
            self.client.get(f"/admin/auth/user/{staff_user.pk}/change/"),
            'id="id_profile-TOTAL_FORMS"',
        )
        empty_data = {
            "profile-TOTAL_FORMS": "1",
            "profile-INITIAL_FORMS": "0",
            "profile-MIN_NUM_FORMS": "0",
            "profile-MAX_NUM_FORMS": "1",
            "profile-0-person": "",
            "profile-0-role": "",
            "profile-0-primary_unit": "",
            "profile-0-inherit_descendants": "",
            "profile-0-is_active_admin": "",
        }
        formset = formset_class(data=empty_data, instance=staff_user, prefix="profile")
        self.assertFalse(formset.is_valid())
        self.assertIn("perfil administrativo ativo", formset.non_form_errors()[0])

        valid_data = {
            **empty_data,
            "profile-0-role": Profile.AdminRole.UNIT_COORDINATOR,
            "profile-0-primary_unit": str(self.latec.pk),
            "profile-0-is_active_admin": "on",
        }
        self.assertTrue(formset_class(data=valid_data, instance=staff_user, prefix="profile").is_valid())

        superuser = get_user_model().objects.create_superuser("profileless_superuser", password="password")
        self.assertTrue(formset_class(data=empty_data, instance=superuser, prefix="profile").is_valid())


class RemovedRoleMigrationTests(TestCase):
    def test_removed_profiles_are_deactivated_without_demoting_native_superusers(self):
        users = []
        for role in ("admin", "editor", "reader"):
            user = get_user_model().objects.create_user(f"legacy_{role}", is_staff=True)
            Profile.objects.create(user=user, role=role)
            users.append(user)
        superuser = get_user_model().objects.create_superuser(
            "legacy_superuser",
            "legacy-super@example.com",
            "password",
        )
        Profile.objects.create(user=superuser, role="admin")

        migration = importlib.import_module("apps.accounts.migrations.0003_alter_profile_role")
        migration.deactivate_removed_roles(
            django_apps,
            SimpleNamespace(connection=connection),
        )

        for user in users:
            user.refresh_from_db()
            user.profile.refresh_from_db()
            self.assertFalse(user.is_staff)
            self.assertFalse(user.profile.is_active_admin)
            self.assertEqual(user.profile.role, Profile.AdminRole.UNIT_COORDINATOR)
        superuser.refresh_from_db()
        superuser.profile.refresh_from_db()
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertFalse(superuser.profile.is_active_admin)
