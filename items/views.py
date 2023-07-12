from django.contrib.auth.forms import (
    AuthenticationForm,
)
from django.core.paginator import Paginator
from django.db.models import (
    Q,
    CharField,
    F,
)
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import User
from rest_framework import viewsets, permissions
from .forms import (
    UserForm,
    VersionForm,
    ScreenshotForm,
    ItemForm,
    ReviewForm,
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

from .utils import (
    get_filtered_items,
    PAGE_SIZE,
    page_out_of_bounds,
)
from django.db.models import Prefetch


CharField.register_lookup(Lower)


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


def items(request):
    page_obj = get_filtered_items(request=request)

    if page_out_of_bounds(request, page_obj):
        return redirect("home")

    return render(request, "items.html", {"page_obj": page_obj})


def scenario(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    page_obj = get_filtered_items(request=request, tc=item.id)

    if page_out_of_bounds(request, page_obj):
        return redirect("scenario", item_permalink)

    return render(request, "items.html", {"page_obj": page_obj, "scenario": item})


def tags(request):
    tags = Tag.objects.all().order_by("-count")
    return render(request, "tags.html", {"tags": tags})


def tag(request, name):
    tag = get_object_or_404(Tag, name=name)
    page_obj = get_filtered_items(request=request, tag=tag)

    if page_out_of_bounds(request, page_obj):
        return redirect("tag", name)

    return render(request, "items.html", {"page_obj": page_obj, "tag": tag})


def item_detail(request, item_permalink):
    legacy_tc_slugs = ["marathon", "marathon-2-durandal", "marathon-infinity"]

    if item_permalink in legacy_tc_slugs:
        url = reverse("scenario", args=[item_permalink])
        query_string = request.META.get("QUERY_STRING", "")
        if query_string:
            url = f"{url}?{query_string}"
        return redirect(url, permanent=True)

    item = get_object_or_404(
        Item.objects.select_related(
            "user",
        ).prefetch_related(
            "screenshots",
            "tags",
            Prefetch(
                "versions",
                queryset=Version.objects.order_by("-created_at").prefetch_related(
                    Prefetch(
                        "reviews",
                        queryset=Review.objects.order_by("-created_at").select_related("user"),
                    )
                ),
                to_attr="ordered_versions",
            ),
        ),
        permalink=item_permalink,
    )

    item_version = item.ordered_versions[0] if item.ordered_versions else None

    if item_version is None:
        if item.user_id == request.user.id:
            return redirect("add_version", item_permalink)
        else:
            return redirect("home")

    item_screenshots = list(item.screenshots.all())

    item_reviews = []
    for version in item.ordered_versions:
        item_reviews.extend(version.reviews.all())

    item_tags = list(item.tags.all())

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
    paginator = Paginator(reviews, PAGE_SIZE)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if page_out_of_bounds(request, page_obj):
        return redirect("reviews")

    return render(
        request,
        "reviews.html",
        {
            "page_obj": page_obj,
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


def log_out(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")


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

                next_url = request.GET.get("next", "home")
                return redirect(next_url)

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
    items = get_filtered_items(request=request, user=show_user)

    if request.user.is_authenticated:
        if request.user == show_user:
            items = get_filtered_items(
                request=request, items=Item.objects, user=show_user
            )

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
            form.instance.user = request.user
            form.save()
            return redirect("add_version", item_permalink=item.permalink)
    else:
        form = ItemForm()
    return render(request, "simple_form.html", {"form": form, "title": "Add Item"})


def add_item_child(request, item_permalink, model_name, form_class):
    item = get_object_or_404(Item, permalink=item_permalink)

    if (item.user != request.user) and (not request.user.is_staff):
        messages.error(
            request, "You do not have permission to add a version to this item."
        )
        return redirect("item_detail", item_permalink=item.permalink)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        form.instance.item = item
        form.instance.user = request.user

        if form.is_valid():
            form.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = form_class()

    return render(
        request, "simple_form.html", {"form": form, "title": f"Add {model_name}"}
    )


@login_required
def add_version(request, item_permalink):
    return add_item_child(request, item_permalink, "Version", VersionForm)


@login_required
def add_screenshot(request, item_permalink):
    return add_item_child(request, item_permalink, "Screenshot", ScreenshotForm)


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


def item_download(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    version = Version.objects.filter(item=item).order_by("-created_at").first()

    if version is None:
        messages.error(request, "No version available for download")
        return redirect("home")

    Version.objects.filter(id=version.id).update(
        downloads_count=F("downloads_count") + 1
    )
    Item.objects.filter(id=item.id).update(downloads_count=F("downloads_count") + 1)

    if version.file:
        return redirect(version.file.url)

    if version.link:
        return redirect(version.link)

    messages.error(request, "No file or URL found")
    return redirect("home")


@login_required
def item_delete(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)

    # Check if the user is the owner of the item
    if request.user != item.user:
        return redirect("item_detail", item_permalink=item.permalink)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item deleted successfully")
        return redirect("home")
    return render(request, "item_confirm_delete.html", {"item": item})


@login_required
def new_item_review(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.instance.version = item.find_version()
            form.instance.user = request.user
            form.save()
            return redirect("item_detail", item_permalink=item.permalink)
    else:
        form = ReviewForm()
    return render(request, "simple_form.html", {"form": form, "title": "Add Review"})


def items_redirect(request):
    query_string = request.META["QUERY_STRING"]
    if query_string:
        return redirect(f"/?{query_string}")
    else:
        return redirect("/")
