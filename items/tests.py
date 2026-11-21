from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from .models import Item, Review, Screenshot, Tag, User, Version


@override_settings(DISCORD_BOT_TOKEN=None)
class SmokeTests(TestCase):
    """Render every public page and the main logged-in pages.

    Requests use secure=True because SECURE_SSL_REDIRECT is on outside DEBUG.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="leela", password="pw-for-tests-only", first_name="Leela"
        )
        cls.tag = Tag.objects.create(name="netmaps")
        for name, permalink in settings.SCENARIOS.items():
            item = Item.objects.create(name=name, body=name, user=cls.user)
            # save() derives the permalink from the name; production's differ.
            Item.objects.filter(pk=item.pk).update(permalink=permalink)
        cls.item = Item.objects.create(
            name="Test Map", body="A **map**.", user=cls.user
        )
        cls.item.tags.add(cls.tag)
        cls.version = Version.objects.create(
            item=cls.item, name="1.0", link="https://example.com/map.zip"
        )
        cls.review = Review.objects.create(
            version=cls.version,
            user=cls.user,
            title="Great",
            body="Fun map.",
            rating=5,
        )

    def get(self, url, **kwargs):
        return self.client.get(url, secure=True, **kwargs)

    def assertPagesOk(self, urls):
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.get(url).status_code, 200)

    def test_public_pages(self):
        p = self.item.permalink
        self.assertPagesOk(
            [
                "/",
                "/?order=popular",
                "/?search=map",
                "/scenarios/",
                "/tags/",
                f"/tags/{self.tag.permalink}/",
                f"/items/{p}/",
                f"/items/{p}/reviews/{self.review.id}",
                "/reviews/",
                "/users/",
                f"/users/{self.user.username}/",
                "/login/",
                "/signup/",
                "/sitemap.xml",
                "/items.rss",
                "/reviews.rss",
                "/api/",
                "/terminal/login/",
            ]
        )

    def test_logged_in_pages(self):
        self.client.force_login(self.user)
        p = self.item.permalink
        self.assertPagesOk(
            [
                "/settings/",
                "/items/new",
                f"/items/{p}/edit",
                f"/items/{p}/versions/new",
                f"/items/{p}/reviews/{self.review.id}/edit",
                f"/items/{p}/screenshots/new",
            ]
        )

    def test_admin(self):
        admin = User.objects.create_superuser(
            username="admin", password="pw-for-tests-only"
        )
        self.client.force_login(admin)
        self.assertPagesOk(
            [
                "/terminal/",
                "/terminal/items/item/",
                f"/terminal/items/item/{self.item.pk}/change/",
            ]
        )

    def test_download_redirects_to_link(self):
        response = self.get(reverse("item_download", args=[self.item.permalink]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://example.com/map.zip")

    def test_https(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response["Location"].startswith("https://"))
        self.assertIn("max-age=31536000", self.get("/")["Strict-Transport-Security"])

    def test_www_redirects_to_apex(self):
        response = self.client.get(
            "/", secure=True, headers={"host": "www.simplici7y.com"}
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://simplici7y.com/")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ScreenshotTests(TestCase):
    def test_thumbnails_render(self):
        user = User.objects.create_user(username="durandal", password="x")
        item = Item.objects.create(name="Shot Map", body="b", user=user)
        buf = io.BytesIO()
        Image.new("RGBA", (1200, 900), (255, 0, 0, 128)).save(buf, "PNG")
        shot = Screenshot.objects.create(
            item=item, file=SimpleUploadedFile("shot.png", buf.getvalue())
        )
        thumb = Image.open(shot.file_thumb)
        self.assertEqual(thumb.format, "JPEG")
        self.assertLessEqual(thumb.size[0], 300)
        self.assertEqual(Image.open(shot.file_content).size, (920, 690))
