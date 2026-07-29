from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0003_alter_project_options_remove_project_display_order_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectStartupProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                ("focus_area", models.CharField(max_length=180)),
                ("species_or_subject", models.CharField(blank=True, max_length=220)),
                ("institution", models.CharField(blank=True, max_length=220)),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="startup_profile",
                        to="portfolio.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "perfil de startup do projeto",
                "verbose_name_plural": "perfis de startup dos projetos",
            },
        ),
    ]
