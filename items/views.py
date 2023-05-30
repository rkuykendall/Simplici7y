from django.shortcuts import render
from rest_framework import viewsets
from .models import Item, Version, Download, Review, Screenshot, Tag
from .serializers import (
    ItemSerializer,
    VersionSerializer,
    DownloadSerializer,
    ReviewSerializer,
    ScreenshotSerializer,
    TagSerializer,
)


# Create your views here.
def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


def item_list(request):
    items = Item.objects.all()
    return render(request, "item_list.html", {"items": items})


class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
