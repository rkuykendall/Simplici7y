from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import User
from rest_framework import viewsets, permissions
from .forms import UserForm
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


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


# @login_required  # Remove after go-live
def items(request):
    latest_versions = Prefetch(
        "version_set",
        queryset=Version.objects.order_by("-created_at"),
        to_attr="latest_version",
    )
    random_screenshots = Prefetch(
        "screenshot_set",
        queryset=Screenshot.objects.order_by("?"),
        to_attr="random_screenshot",
    )

    item_objects = Item.objects.prefetch_related(
        latest_versions, random_screenshots, "user"
    ).order_by("-created_at")
    paginator = Paginator(item_objects, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "items.html", {"page_obj": page_obj})


# @login_required  # Remove after go-live
def item_detail(request, item_permalink):
    item = get_object_or_404(
        Item.objects.annotate(total_downloads=Count("version__download")),
        permalink=item_permalink,
    )
    # item.prefetch_related('version_set', 'screenshot_set', 'review_set')
    item_version = item.find_version()
    item_screenshots = Screenshot.objects.filter(item=item).all()
    item_reviews = Review.objects.filter(version__item=item).all()

    return render(
        request,
        "item_detail.html",
        {
            "item": item,
            "screenshots": item_screenshots,
            "version": item_version,
            "reviews": item_reviews,
        },
    )


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


# @login_required  # Remove after go-live
def reviews(request):
    return render(request, "reviews.html")


# @login_required  # Remove after go-live
def users(request):
    return render(request, "users.html")


# @login_required
def submit(request):
    return render(request, "submit.html")


@login_required
def settings(request):
    return render(request, "settings.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


# @login_required  # Remove after go-live
def about(request):
    return render(request, "about.html")


@login_required  # Remove after go-live
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("items")
    else:
        form = UserForm()

    return render(request, "signup.html", {"form": form})


@login_required  # Remove after go-live
def login_view(request):
    # You would generally use Django's built-in views for this.
    pass


# @login_required  # Remove after go-live
def user(request, username):
    user = User.objects.get(username=username)
    return render(request, "user.html", {"user": user})


def view_404(request):
    return render(request, "404.html")
