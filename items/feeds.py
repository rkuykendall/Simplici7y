from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import path
from markdownify.templatetags.markdownify import markdownify

from items.models import Review, Version
from items.utils import get_filtered_items, PAGE_SIZE


class ItemsFeed(Feed):
    title = f"{settings.SITE_TITLE} Downloads"
    link = f"https://{settings.FEED_HOST}"
    description = f"Latest updates and submissions to {settings.SITE_TITLE}."

    def items(self):
        return Version.objects.order_by("-created_at").prefetch_related("item")[
            :PAGE_SIZE
        ]

    def item_guid(self, obj):
        return f"https://{settings.FEED_HOST}/items/{obj.item.permalink}/versions/{obj.id}/"

    def item_link(self, version):
        return f"https://{settings.FEED_HOST}/items/{version.item.permalink}/"

    def item_title(self, version):
        return version.item.name

    def item_description(self, version):
        return markdownify(version.item.body)


class ReviewsFeed(Feed):
    title = f"{settings.SITE_TITLE} Reviews"
    link = f"https://{settings.FEED_HOST}/reviews/"
    description = f"Latest reviews on {settings.SITE_TITLE}."

    item_guid_is_permalink = False

    def items(self):
        return Review.objects.order_by("-created_at")[:PAGE_SIZE]

    def item_guid(self, obj):
        return f"https://{settings.FEED_HOST}/items/{obj.version.item.permalink}/reviews/{obj.id}"

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdownify(item.body)


feed_paths = [
    path("items.rss", ItemsFeed()),
    path("reviews.rss", ReviewsFeed()),
]
