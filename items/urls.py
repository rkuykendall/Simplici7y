from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    ItemViewSet,
    VersionViewSet,
    DownloadViewSet,
    ReviewViewSet,
    ScreenshotViewSet,
    TagViewSet,
    item_list,
    item_detail,
)

router = DefaultRouter()
router.register(r"items", ItemViewSet)
router.register(r"versions", VersionViewSet)
router.register(r"downloads", DownloadViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"screenshots", ScreenshotViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    # path("", item_list, name="homepage"),
    path("items/", item_list, name="item_list"),
    path("items/<str:item_permalink>/", item_detail, name="item_detail"),
    path("api/", include(router.urls)),
]
