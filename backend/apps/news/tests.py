import importlib
from types import SimpleNamespace

from django.apps import apps as django_apps
from django.db import connection
from django.template import Context, Template
from django.test import TestCase

from apps.institutional.models import InstitutionalUnit
from apps.news.models import Post, PostLink


SLUG_MIGRATION = importlib.import_module(
    "apps.news.migrations.0004_rename_latecin_post_slugs"
)


class PostSlugMigrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unit = InstitutionalUnit.objects.create(
            name="LABTEC.IN",
            acronym="LABTEC.IN",
            slug="labtec-in-slug-migration",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )

    def create_post(self, slug):
        return Post.objects.create(
            unit=self.unit,
            title=slug,
            slug=slug,
            content="Conteúdo",
        )

    def test_forward_and_reverse_rename_only_the_exact_legacy_slugs(self):
        unaffected = self.create_post("slug-sem-compatibilidade")
        legacy_posts = {
            source: self.create_post(source)
            for source in SLUG_MIGRATION.SLUG_RENAMES
        }

        schema_editor = SimpleNamespace(connection=connection)
        SLUG_MIGRATION.rename_latecin_slugs(django_apps, schema_editor)

        for source, destination in SLUG_MIGRATION.SLUG_RENAMES.items():
            legacy_posts[source].refresh_from_db()
            self.assertEqual(legacy_posts[source].slug, destination)
        unaffected.refresh_from_db()
        self.assertEqual(unaffected.slug, "slug-sem-compatibilidade")

        SLUG_MIGRATION.restore_latecin_slugs(django_apps, schema_editor)

        for source, post in legacy_posts.items():
            post.refresh_from_db()
            self.assertEqual(post.slug, source)

    def test_preflight_reports_source_and_destination_ids_on_collision(self):
        source, destination = next(iter(SLUG_MIGRATION.SLUG_RENAMES.items()))
        source_post = self.create_post(source)
        destination_post = self.create_post(destination)

        with self.assertRaisesMessage(
            RuntimeError,
            f"source ID {source_post.id} ({source}) conflicts with "
            f"destination ID {destination_post.id} ({destination})",
        ):
            SLUG_MIGRATION.rename_latecin_slugs(
                django_apps,
                SimpleNamespace(connection=connection),
            )

        source_post.refresh_from_db()
        self.assertEqual(source_post.slug, source)


class PostContentTemplateTagTests(TestCase):
    def test_escapes_editorial_html_and_links_registered_labels(self):
        unit = InstitutionalUnit.objects.create(
            name="LABTEC.IN",
            acronym="LABTEC.IN",
            slug="labtec-in-post-content",
            unit_type=InstitutionalUnit.UnitType.LABORATORY,
        )
        post = Post.objects.create(
            unit=unit,
            title="Notícia",
            slug="noticia-com-link",
            content="<script>alert('xss')</script> Congresso externo",
        )
        PostLink.objects.create(
            post=post,
            label="Congresso externo",
            url="https://example.com/congresso",
        )

        rendered = Template("{% load news_content %}{{ post|post_content }}").render(Context({"post": post}))

        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn('href="https://example.com/congresso"', rendered)
