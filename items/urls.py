from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .feeds import feed_paths
from .sitemaps import sitemaps
from .views import (
    api_paths,
    session_paths,
    item_paths,
)

urlpatterns = (
    [
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
