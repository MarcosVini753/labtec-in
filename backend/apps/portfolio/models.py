from django.db import models

from apps.common.models import BaseModel, EditorialStatus


class ProjectCategory(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name = "categoria de projeto"
        verbose_name_plural = "categorias de projeto"

    def __str__(self) -> str:
        return self.name


class ProjectStatus(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name = "status de projeto"
        verbose_name_plural = "status de projeto"

    def __str__(self) -> str:
        return self.name


class Project(BaseModel):
    unit = models.ForeignKey(
        "institutional.InstitutionalUnit",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    axis = models.ForeignKey("axes.ResearchAxis", on_delete=models.SET_NULL, related_name="projects", blank=True, null=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, related_name="projects", blank=True, null=True)
    area = models.CharField(max_length=160, blank=True)
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, related_name="projects", blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    summary = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="portfolio/projects/", blank=True)
    editorial_status = models.CharField(max_length=32, choices=EditorialStatus.choices, default=EditorialStatus.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    include_in_parent_ecosystem = models.BooleanField(
        default=False,
        help_text="Inclui este conteúdo no recorte público da unidade mãe.",
    )
    team = models.ManyToManyField("people.Person", through="ProjectTeamMember", related_name="projects", blank=True)

    class Meta:
        ordering = ("-year", "title")
        verbose_name = "projeto"
        verbose_name_plural = "projetos"

    def __str__(self) -> str:
        return self.title


class ProjectStartupProfile(BaseModel):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="startup_profile",
    )
    focus_area = models.CharField(max_length=180)
    species_or_subject = models.CharField(max_length=220, blank=True)
    institution = models.CharField(max_length=220, blank=True)

    class Meta:
        verbose_name = "perfil de startup do projeto"
        verbose_name_plural = "perfis de startup dos projetos"

    def __str__(self) -> str:
        return f"Startup: {self.project}"


class ProjectTeamMember(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="team_members")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="project_memberships")
    role = models.CharField(max_length=120, blank=True)
    is_lead = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "person__full_name")
        constraints = [
            models.UniqueConstraint(fields=("project", "person"), name="unique_project_team_member"),
        ]
        verbose_name = "membro de equipe de projeto"
        verbose_name_plural = "membros de equipe de projeto"

    def __str__(self) -> str:
        return f"{self.person} em {self.project}"


class ProjectResult(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="results")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    result_type = models.CharField(max_length=80, blank=True)
    file = models.FileField(upload_to="portfolio/results/", blank=True)
    external_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "title")
        verbose_name = "resultado de projeto"
        verbose_name_plural = "resultados de projeto"

    def __str__(self) -> str:
        return self.title


class ProjectLink(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=120)
    url = models.URLField()
    link_type = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "label")
        verbose_name = "link de projeto"
        verbose_name_plural = "links de projeto"

    def __str__(self) -> str:
        return self.label
