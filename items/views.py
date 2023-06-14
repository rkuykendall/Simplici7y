from django.contrib.auth.forms import (
    AuthenticationForm,
)
from django.contrib.postgres.search import TrigramSimilarity
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
from .forms import (
    UserForm,
    VersionForm,
    ScreenshotForm,
    ItemForm,
)
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
from django.contrib import messages

CharField.register_lookup(Lower)

page_size = 20


def get_items_with_versions():
    return Item.objects.exclude(version_created_at__isnull=True)


def order_items(items, order):
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
    return items


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


def get_filtered_items(request, items=None, tc=None, tag=None, user=None):
    items = items or get_items_with_versions()

    if tc:
        items = items.filter(tc=tc)

    if tag:
        items = items.filter(tags=tag)

    if user:
        items = items.filter(user=user)

    latest_version = Prefetch(
        "versions",
        queryset=Version.objects.order_by("-created_at"),
        to_attr="latest_version",
    )

    random_screenshots = Prefetch(
        "screenshots",
        queryset=Screenshot.objects.order_by("?"),
        to_attr="random_screenshot",
    )

    items = items.prefetch_related(latest_version, random_screenshots, "user")

    order = request.GET.get("order")
    search = request.GET.get("search", None)

    if search:
        if len(search) < 4:
            items = items.filter(Q(name__icontains=search))
        else:
            items = (
                items.annotate(
                    similarity=TrigramSimilarity("name", search),
                )
                .filter(similarity__gt=0.1)
                .order_by("-similarity")
            )

    if order or not search:
        items = order_items(items, order)

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
        Item,
        permalink=item_permalink,
    )

    item_version = item.find_version()
    item_screenshots = Screenshot.objects.filter(item=item).order_by("created_at").all()
    item_reviews = (
        Review.objects.filter(version__item=item).order_by("-created_at").all()
    ).prefetch_related(
        "version",
        "user",
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


# def item_edit(request, item_permalink):
#     item = get_object_or_404(Item, permalink=item_permalink)
#     if request.method == "POST":
#         form = ItemForm(request.POST, instance=item)
#         if form.is_valid():
#             form.save()
#             return redirect("item", item_permalink=item.permalink)
#     else:
#         form = ItemForm(instance=item)
#     return render(request, "item_form.html", {"form": form, "item": item})


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


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

    return render(
        request,
        "reviews.html",
        {
            "page_obj": page_obj,
            "get_url": get_url,
            "show_item_link": True,
        },
    )


def users(request):
    active_users = (
        User.objects.filter(Q(items_count__gt=0) | Q(reviews_count__gt=0))
        .annotate(total_contributions=F("items_count") + F("reviews_count"))
        .order_by("-total_contributions")
    )

    return render(request, "users.html", {"users": active_users})


# @login_required
def log_out(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
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
            return redirect("home")
    else:
        form = UserForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(
        request=request, template_name="login.html", context={"login_form": form}
    )


def user(request, username):
    User = get_user_model()
    show_user = get_object_or_404(User, username=username)
    items = get_filtered_items(request, user=show_user)

    reviews = (
        Review.objects.filter(user=show_user)
        .order_by("-created_at")
        .prefetch_related(
            "version",
            "user",
        )
    )

    return render(
        request,
        "user.html",
        {
            "show_item_link": True,
            "show_user": show_user,
            "items": items,
            "reviews": reviews,
        },
    )


def view_404(request):
    return render(request, "404.html")


@login_required
def settings(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
    else:
        form = UserForm(instance=user)

    return render(request, "simple_form.html", {"form": form, "title": "User Settings"})


@login_required
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = ItemForm()
    return render(request, "simple_form.html", {"form": form, "title": "Add Item"})


@login_required
def add_version(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    if request.method == "POST":
        form = VersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.item = item
            version.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = VersionForm()
    return render(request, "simple_form.html", {"form": form, "title": "Add Version"})


@login_required
def add_screenshot(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    if request.method == "POST":
        form = ScreenshotForm(request.POST, request.FILES)
        if form.is_valid():
            screenshot = form.save(commit=False)
            screenshot.item = item
            screenshot.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = ScreenshotForm()
    return render(
        request, "simple_form.html", {"form": form, "title": "Add Screenshot"}
    )


@login_required
def version_edit(request, item_permalink, version_id):
    version = get_object_or_404(Version, id=version_id)

    # Check if the user is the owner of the version
    if request.user != version.item.user:
        return redirect("item_detail", item_permalink=version.item.permalink)

    if request.method == "POST":
        form = VersionForm(request.POST, instance=version)
        if form.is_valid():
            form.save()
            return redirect("item_detail", item_permalink=version.item.permalink)
    else:
        form = VersionForm(instance=version)
    return render(request, "simple_form.html", {"form": form, "title": "Edit Version"})


@login_required
def item_edit(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)

    # Check if the user is the owner of the item
    if request.user != item.user:
        return redirect("item_detail", item_permalink=item.permalink)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = ItemForm(instance=item)
    return render(request, "simple_form.html", {"form": form, "title": "Edit Item"})


@login_required
def item_delete(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)

    # Check if the user is the owner of the item
    if request.user != item.user:
        return redirect("item_detail", item_permalink=item.permalink)

    if request.method == "POST":
        item.delete()
        return redirect("items")
    return render(request, "item_confirm_delete.html", {"item": item})


def items_redirect(request):
    query_string = request.META["QUERY_STRING"]
    if query_string:
        return redirect(f"/?{query_string}")
    else:
        return redirect("/")
