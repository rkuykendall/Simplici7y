from django.urls import path, include
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from ..models import Item, Version, Review, Screenshot, Tag
from ..serializers import (
    ItemSerializer,
    VersionSerializer,
    ReviewSerializer,
    ScreenshotSerializer,
    TagSerializer,
)


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.order_by("id").prefetch_related("tags")
    serializer_class = ItemSerializer


class VersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Version.objects.order_by("id")
    serializer_class = VersionSerializer


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.order_by("id")
    serializer_class = ReviewSerializer


class ScreenshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Screenshot.objects.order_by("id")
    serializer_class = ScreenshotSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.order_by("id")
    serializer_class = TagSerializer


router = DefaultRouter()
router.register(r"items", ItemViewSet)
router.register(r"versions", VersionViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"screenshots", ScreenshotViewSet)
router.register(r"tags", TagViewSet)
api_paths = [path("api/", include(router.urls))]
