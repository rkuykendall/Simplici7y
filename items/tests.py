from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

import io
import json
import re
import tempfile
from unittest import mock
from urllib.parse import urlsplit

from django.core import mail

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from PIL import Image

from .models import Item, Review, Screenshot, Tag, User, Version
from .templatetags.helpers import canonical_url
from .utils import MIN_ITEMS_TO_INDEX_TAG


@override_settings(DISCORD_BOT_TOKEN=None)
class SiteTestCase(TestCase):
    """Shared fixture data.

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


class SmokeTests(SiteTestCase):
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


class ApiTests(SiteTestCase):
    def test_endpoints(self):
        for name in ["items", "versions", "reviews", "screenshots", "tags"]:
            with self.subTest(name=name):
                response = self.get(f"/api/{name}/")
                self.assertEqual(response.status_code, 200)
                self.assertIn("results", response.json())
        item = self.get(f"/api/items/{self.item.pk}/").json()
        self.assertEqual(item["name"], "Test Map")

    def test_read_only(self):
        self.client.force_login(self.user)
        url = f"/api/items/{self.item.pk}/"
        self.assertEqual(self.client.delete(url, secure=True).status_code, 405)
        self.assertEqual(
            self.client.post("/api/items/", {}, secure=True).status_code, 405
        )
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    def test_downloads_not_exposed(self):
        self.assertEqual(self.get("/api/downloads/").status_code, 404)


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
        with Image.open(shot.file_thumb) as thumb:
            self.assertEqual(thumb.format, "JPEG")
            self.assertLessEqual(thumb.size[0], 300)
        with Image.open(shot.file_content) as content:
            self.assertEqual(content.size, (920, 690))


class ErrorLoggingTests(TestCase):
    def test_unhandled_exception_is_logged(self):
        with self.assertLogs("django.request", level="ERROR"):
            self.client.raise_request_exception = False
            with self.settings(ROOT_URLCONF="items.tests_urls"):
                response = self.client.get("/boom/", secure=True)
        self.assertEqual(response.status_code, 500)


class SeoTests(SiteTestCase):
    ROBOTS = '<meta name="robots" content="noindex">'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.big_tag = Tag.objects.create(name="Big Tag")
        for i in range(MIN_ITEMS_TO_INDEX_TAG):
            item = Item.objects.create(name=f"Popular {i}", body="b", user=cls.user)
            Version.objects.create(item=item, link="https://example.com")
            item.tags.add(cls.big_tag)
        cls.lurker = User.objects.create_user(username="lurker", password="x")

    def test_sitemap_keeps_only_substantial_pages(self):
        body = self.get("/sitemap.xml").content.decode()
        self.assertIn("/tags/Big%20Tag/", body)
        self.assertNotIn(f"/tags/{self.tag.name}/", body)
        self.assertIn(f"/users/{self.user.username}/", body)
        self.assertNotIn("/users/lurker/", body)
        self.assertNotIn("/login/", body)
        self.assertNotIn("/signup/", body)
        self.assertIn(f"/items/{self.item.permalink}/", body)

    def test_sitemap_tag_urls_resolve(self):
        self.assertEqual(self.get("/tags/Big%20Tag/").status_code, 200)

    def test_noindex_on_thin_pages(self):
        for url in [
            f"/tags/{self.tag.name}/",
            "/users/lurker/",
            "/login/",
            "/signup/",
            "/?search=map",
        ]:
            with self.subTest(url=url):
                self.assertContains(self.get(url), self.ROBOTS)

    def test_indexable_pages(self):
        for url in ["/", "/tags/Big%20Tag/", f"/users/{self.user.username}/"]:
            with self.subTest(url=url):
                self.assertNotContains(self.get(url), self.ROBOTS)

    def test_canonical_drops_sort_and_search(self):
        canonical = (
            '<link rel="canonical" href="https://simplici7y.com/tags/netmaps/" />'
        )
        self.assertContains(self.get("/tags/netmaps/?order=best"), canonical)
        for query, expected in [
            ("?order=best&page=2", "?page=2"),
            ("?page=1", ""),
            ("?page=abc", ""),
            ("?search=x", ""),
        ]:
            with self.subTest(query=query):
                request = RequestFactory().get("/" + query)
                self.assertEqual(
                    canonical_url({"request": request}),
                    "https://simplici7y.com/" + expected,
                )


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class InlineThread:
    def __init__(self, target, args):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


@override_settings(
    DISCORD_BOT_TOKEN="test-token",
    DISCORD_UPLOADS_CHANNEL_ID="111",
    DISCORD_REVIEWS_CHANNEL_ID="222",
)
@mock.patch("items.signals.threading.Thread", InlineThread)
@mock.patch("items.signals.urllib.request.urlopen")
class DiscordTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with override_settings(DISCORD_BOT_TOKEN=None):
            cls.user = User.objects.create_user(username="pfhor", password="x")
            cls.item = Item.objects.create(name="Pfhor Map", body="b", user=cls.user)

    def calls(self, urlopen):
        return [
            (c.args[0].full_url, json.loads(c.args[0].data))
            for c in urlopen.call_args_list
        ]

    def test_new_version_posts_and_publishes(self, urlopen):
        urlopen.side_effect = lambda *a, **k: FakeResponse(b'{"id": "999"}')
        with self.assertNoLogs("items.signals"):
            with self.captureOnCommitCallbacks(execute=True):
                version = Version.objects.create(item=self.item, link="https://x.com")
        api = "https://discord.com/api/v10/channels/111/messages"
        self.assertEqual(
            self.calls(urlopen),
            [
                (
                    api,
                    {"content": f"https://simplici7y.com/items/{self.item.permalink}/"},
                ),
                (f"{api}/999/crosspost", {}),
            ],
        )
        request = urlopen.call_args_list[0].args[0]
        self.assertEqual(request.get_header("Authorization"), "Bot test-token")
        self.assertEqual(urlopen.call_args_list[0].kwargs["timeout"], 10)

        urlopen.reset_mock()
        version.name = "edited"
        with self.captureOnCommitCallbacks(execute=True):
            version.save()
        urlopen.assert_not_called()

    def test_new_review_posts_to_reviews_channel(self, urlopen):
        urlopen.side_effect = lambda *a, **k: FakeResponse(b'{"id": "999"}')
        with override_settings(DISCORD_BOT_TOKEN=None):
            version = Version.objects.create(item=self.item, link="https://x.com")
        with self.captureOnCommitCallbacks(execute=True):
            Review.objects.create(
                version=version, user=self.user, title="t", body="b", rating=4
            )
        self.assertTrue(self.calls(urlopen)[0][0].endswith("/channels/222/messages"))

    def test_nothing_sent_until_commit(self, urlopen):
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            Version.objects.create(item=self.item, link="https://x.com")
        urlopen.assert_not_called()
        self.assertEqual(len(callbacks), 1)

    def test_failure_is_logged_not_raised(self, urlopen):
        urlopen.side_effect = OSError("discord down")
        with self.assertLogs("items.signals", level="ERROR"):
            with self.captureOnCommitCallbacks(execute=True):
                Version.objects.create(item=self.item, link="https://x.com")

    def test_no_token_sends_nothing(self, urlopen):
        with override_settings(DISCORD_BOT_TOKEN=None):
            with self.captureOnCommitCallbacks(execute=True):
                Version.objects.create(item=self.item, link="https://x.com")
        urlopen.assert_not_called()


class StaticFilesTests(TestCase):
    def test_collectstatic_with_production_storage(self):
        """Catches CSS url() references to files that don't exist."""
        manifest = "whitenoise.storage.CompressedManifestStaticFilesStorage"
        with tempfile.TemporaryDirectory() as root:
            with override_settings(
                STATIC_ROOT=root,
                STORAGES={**settings.STORAGES, "staticfiles": {"BACKEND": manifest}},
            ):
                call_command("collectstatic", interactive=False, verbosity=0)
                from django.contrib.staticfiles.storage import staticfiles_storage

                staticfiles_storage._setup()
                self.assertRegex(
                    staticfiles_storage.url("css/global.css"),
                    r"^/static/css/global\.[0-9a-f]{12}\.css$",
                )


class PasswordResetTests(TestCase):
    def test_reset_flow_sends_email_and_changes_password(self):
        user = User.objects.create_user(
            username="tycho", email="tycho@example.com", password="old-password-1"
        )
        response = self.client.post(
            "/password_reset/", {"email": "tycho@example.com"}, secure=True
        )
        self.assertRedirects(
            response, "/password_reset/done/", fetch_redirect_response=False
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "leela@simplici7y.com")

        link = re.search(r"https?://\S+/reset/\S+/", mail.outbox[0].body).group(0)
        path = urlsplit(link).path
        response = self.client.get(path, secure=True)  # redirects to set-password
        new_password = "n3w-Pa55word-for-tests"
        response = self.client.post(
            response["Location"],
            {"new_password1": new_password, "new_password2": new_password},
            secure=True,
        )
        self.assertRedirects(response, "/reset/done/", fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))
