from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Profile(BaseModel):
    class AdminRole(models.TextChoices):
        LAB_COORDINATOR = "lab_coordinator", "Coordenação LABTEC.IN"
        UNIT_COORDINATOR = "unit_coordinator", "Coordenação de unidade"
        MENTOR = "mentor", "Orientador/Professor"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    person = models.OneToOneField(
        "people.Person",
        on_delete=models.SET_NULL,
        related_name="admin_profile",
        blank=True,
        null=True,
    )
    primary_unit = models.ForeignKey(
        "institutional.InstitutionalUnit",
        on_delete=models.SET_NULL,
        related_name="primary_admin_profiles",
        blank=True,
        null=True,
    )
    authorized_units = models.ManyToManyField(
        "institutional.InstitutionalUnit",
        related_name="authorized_admin_profiles",
        blank=True,
    )
    inherit_descendants = models.BooleanField(default=False)
    role = models.CharField(max_length=32, choices=AdminRole.choices)
    is_active_admin = models.BooleanField(default=True)

    class Meta:
        verbose_name = "perfil administrativo"
        verbose_name_plural = "perfis administrativos"

    def __str__(self) -> str:
        return f"{self.user} ({self.get_role_display()})"

    @property
    def is_lab_coordinator(self) -> bool:
        return (
            self.is_active_admin
            and self.role == self.AdminRole.LAB_COORDINATOR
            and self.primary_unit_id is not None
            and self.primary_unit.slug == "labtec-in"
        )

    @property
    def can_publish(self) -> bool:
        return self.is_lab_coordinator

    def accessible_unit_ids(self) -> set[int]:
        """Return the explicit institutional scope for this active profile."""
        if not self.is_active_admin:
            return set()

        from apps.institutional.models import InstitutionalUnit

        if self.role == self.AdminRole.LAB_COORDINATOR:
            if not self.is_lab_coordinator:
                return set()
            root_id = (
                InstitutionalUnit.objects.filter(slug="labtec-in")
                .values_list("pk", flat=True)
                .first()
            )
            unit_ids = {root_id} if root_id else set()
        else:
            unit_ids = set(self.authorized_units.values_list("pk", flat=True))
            if self.primary_unit_id:
                unit_ids.add(self.primary_unit_id)

        if self.role == self.AdminRole.MENTOR:
            latec_id = InstitutionalUnit.objects.filter(slug="latec").values_list("pk", flat=True).first()
            return {latec_id} & unit_ids if latec_id else set()

        should_inherit = self.is_lab_coordinator or (
            self.role == self.AdminRole.UNIT_COORDINATOR and self.inherit_descendants
        )
        if not should_inherit:
            return unit_ids

        pending = list(unit_ids)
        while pending:
            children = set(
                InstitutionalUnit.objects.filter(parent_id__in=pending)
                .exclude(pk__in=unit_ids)
                .values_list("pk", flat=True)
            )
            unit_ids.update(children)
            pending = list(children)
        return unit_ids

    def mentor_axis_ids(self) -> set[int]:
        if not self.is_active_admin or self.role != self.AdminRole.MENTOR or not self.person_id:
            return set()
        return set(
            self.person.axis_mentorships.filter(axis__unit__slug="latec").values_list("axis_id", flat=True)
        )
