from django.contrib.auth import get_user_model
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Item, Tag

User = get_user_model()


class ItemsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return Item.objects.exclude(version_created_at__isnull=True)

    def lastmod(self, obj):
        return obj.version_created_at


class UserSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return User.objects.all()

    def lastmod(self, obj):
        return obj.date_joined


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ["home", "tags", "login", "signup"]

    def location(self, item):
        return reverse(item)


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Tag.objects.all()

    def location(self, item):
        return reverse("tag", args=[item.permalink])


sitemaps = {
    "items": ItemsSitemap,
    "users": UserSitemap,
    "static": StaticViewSitemap,
    "tags": TagSitemap,
}
