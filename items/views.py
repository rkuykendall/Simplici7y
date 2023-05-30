from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from .models import Item, Version, Download, Review, Screenshot, Tag
from .permissions import IsOwnerOrReadOnly
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


@login_required
def item_list(request):
    item_objects = Item.objects.all().order_by("-updated_at")
    paginator = Paginator(item_objects, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "item_list.html", {"page_obj": page_obj})


@login_required
def item_detail(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    return render(request, "item_detail.html", {"item": item})


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
