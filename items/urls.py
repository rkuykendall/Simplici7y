from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import path, reverse

from .feeds import feed_paths
from .sitemaps import sitemaps
from .views import (
    api_paths,
    session_paths,
    item_paths,
)


def robots_txt(request):
    # Crawl everything: thin pages are kept out of the index with noindex,
    # which Google can only see if it's allowed to fetch them.
    sitemap_url = settings.CANONICAL_DOMAIN + reverse(
        "django.contrib.sitemaps.views.sitemap"
    )
    return HttpResponse(
        f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n",
        content_type="text/plain",
    )


urlpatterns = (
    [
        path("robots.txt", robots_txt),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
    ]
    + item_paths
    + session_paths
    + feed_paths
    + api_paths
)
