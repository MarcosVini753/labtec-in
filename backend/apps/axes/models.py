from django.db import models

from apps.common.models import BaseModel


class ResearchAxis(BaseModel):
    unit = models.ForeignKey(
        "institutional.InstitutionalUnit",
        on_delete=models.PROTECT,
        related_name="research_axes",
    )
    number = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, help_text="Palavras-chave separadas por vírgula.")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "number")
        verbose_name = "eixo de atuação"
        verbose_name_plural = "eixos de atuação"

    def __str__(self) -> str:
        return f"{self.number}. {self.title}"


class AxisMentorship(BaseModel):
    axis = models.ForeignKey(ResearchAxis, on_delete=models.CASCADE, related_name="mentorships")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="axis_mentorships")
    role = models.CharField(max_length=120, default="Orientador")
    is_main_mentor = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("axis__number", "display_order", "person__full_name")
        constraints = [
            models.UniqueConstraint(fields=("axis", "person"), name="unique_axis_person_mentorship"),
        ]
        verbose_name = "mentoria de eixo"
        verbose_name_plural = "mentorias de eixo"

    def __str__(self) -> str:
        return f"{self.person} em {self.axis}"
