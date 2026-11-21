from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Item
from .utils import indexable_tags, indexable_users


class ItemsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return Item.objects.exclude(version_created_at__isnull=True).order_by("id")

    def lastmod(self, obj):
        return obj.version_created_at


class UserSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return indexable_users().order_by("id")

    def lastmod(self, obj):
        return obj.date_joined


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ["home", "tags", "scenario_list"]

    def location(self, item):
        return reverse(item)


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return indexable_tags().order_by("id")

    def location(self, item):
        # tag_detail looks tags up by name, not permalink.
        return reverse("tag", args=[item.name])


sitemaps = {
    "items": ItemsSitemap,
    "users": UserSitemap,
    "static": StaticViewSitemap,
    "tags": TagSitemap,
}
