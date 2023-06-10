from django.core.paginator import Paginator
from django.db.models import (
    Prefetch,
    Count,
    Q,
    Exists,
    OuterRef,
    CharField,
    F,
)
from django.db.models.functions import Lower
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
from django.contrib.auth import get_user_model
from items.models import Item, Review


CharField.register_lookup(Lower)


page_size = 20


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


def get_filtered_items(request, tc=None, tag=None):
    latest_version = Prefetch(
        "version_set",
        queryset=Version.objects.order_by("-created_at"),
        to_attr="latest_version",
    )
    random_screenshots = Prefetch(
        "screenshot_set",
        queryset=Screenshot.objects.order_by("?"),
        to_attr="random_screenshot",
    )

    items = Item.objects.annotate(
        has_version=Exists(Version.objects.filter(item=OuterRef("pk")))
    )

    if tc:
        items = items.filter(tc=tc)

    if tag:
        items = items.filter(tags=tag)

    items = items.filter(has_version=True).prefetch_related(
        latest_version, random_screenshots, "user"
    )

    order = request.GET.get("order")
    search = request.GET.get("search", None)

    if search:
        items = items.filter(Q(name__unaccent__lower__trigram_similar=search))

    if order == "old":
        items = items.order_by("version_created_at")
    elif order == "reviews":
        items = items.filter(reviews_count__gt=0).order_by("-rating_average")
    elif order == "best":
        items = items.filter(reviews_count__gt=0).order_by("-rating_weighted")
    elif order == "worst":
        items = items.filter(reviews_count__gt=0).order_by("rating_weighted")
    elif order == "loud":
        items = items.filter(reviews_count__gt=0).order_by("-reviews_count")
    elif order == "popular":
        items = items.order_by("-downloads_count")
    else:
        items = items.order_by("-version_created_at")

    paginator = Paginator(items, page_size)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj


def items(request):
    page_obj = get_filtered_items(request)
    return render(request, "items.html", {"page_obj": page_obj})


def scenario(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    page_obj = get_filtered_items(request, tc=item.id)
    return render(request, "items.html", {"page_obj": page_obj, "scenario": item})


def tag(request, name):
    tag = get_object_or_404(Tag, name=name)
    page_obj = get_filtered_items(request, tag=tag)
    return render(request, "items.html", {"page_obj": page_obj, "tag": tag})


def item_detail(request, item_permalink):
    legacy_tc_slugs = ["marathon", "marathon-2-durandal", "marathon-infinity"]

    if item_permalink in legacy_tc_slugs:
        return redirect("scenario", item_permalink, permanent=True)

    item = get_object_or_404(
        Item.objects.annotate(total_downloads=Count("version__download")),
        permalink=item_permalink,
    )
    # item.prefetch_related('version_set', 'screenshot_set', 'review_set')
    item_version = item.find_version()
    item_screenshots = Screenshot.objects.filter(item=item).order_by("created_at").all()
    item_reviews = (
        Review.objects.filter(version__item=item).order_by("-created_at").all()
    )
    item_tags = Tag.objects.filter(item=item).all()

    return render(
        request,
        "item_detail.html",
        {
            "item": item,
            "screenshots": item_screenshots,
            "version": item_version,
            "reviews": item_reviews,
            "tags": item_tags,
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


def reviews(request):
    reviews = Review.objects.order_by("-created_at")
    paginator = Paginator(reviews, page_size)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    base_url = request.path
    query_params = request.GET.copy()

    def get_url(page_number):
        query_params["page"] = page_number
        return f"{base_url}?{query_params.urlencode()}"

    return render(request, "reviews.html", {"page_obj": page_obj, "get_url": get_url})


def users(request):
    active_users = (
        User.objects.filter(Q(items_count__gt=0) | Q(reviews_count__gt=0))
        .annotate(total_contributions=F("items_count") + F("reviews_count"))
        .order_by("-total_contributions")
    )

    return render(request, "users.html", {"users": active_users})


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


def user(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    items_with_versions = Item.objects.annotate(
        has_version=Exists(Version.objects.filter(item=OuterRef("pk")))
    )
    items = items_with_versions.filter(user=user, has_version=True).order_by(
        "-version_created_at"
    )

    reviews = Review.objects.filter(user=user).order_by("-created_at")

    return render(
        request, "user.html", {"user": user, "items": items, "reviews": reviews}
    )


def view_404(request):
    return render(request, "404.html")
