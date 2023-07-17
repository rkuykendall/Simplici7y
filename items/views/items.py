from django.core.paginator import Paginator
from django.db.models import (
    Q,
    CharField,
    F,
    Value,
    BooleanField,
)
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..forms import (
    VersionForm,
    ScreenshotForm,
    ItemForm,
    ReviewForm,
)
from ..models import Item, Version, Download, Review, Screenshot, Tag
from django.contrib.auth import get_user_model
from django.contrib import messages

from ..utils import (
    get_filtered_items,
    PAGE_SIZE,
    page_out_of_bounds,
)
from django.db.models import Prefetch


CharField.register_lookup(Lower)


def items_list_redirect(request):
    # Redirects /items/ to /
    query_string = request.META["QUERY_STRING"]
    if query_string:
        return redirect(f"/?{query_string}")
    else:
        return redirect("/")


def item_list(request):
    page_obj = get_filtered_items(request=request)

    if page_out_of_bounds(request, page_obj):
        return redirect("home")

    return render(request, "items.html", {"page_obj": page_obj})


def scenario_detail(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    page_obj = get_filtered_items(request=request, tc=item.id)

    if page_out_of_bounds(request, page_obj):
        return redirect("scenario", item_permalink)

    return render(request, "items.html", {"page_obj": page_obj, "scenario": item})


def tag_list(request):
    tags = Tag.objects.all().order_by("-count")
    return render(request, "tags.html", {"tags": tags})


def tag_detail(request, name):
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
                        queryset=Review.objects.order_by("-created_at").select_related(
                            "user"
                        ),
                    )
                ),
                to_attr="ordered_versions",
            ),
        ),
        permalink=item_permalink,
    )

    user_has_permission = item.has_permission(request.user)
    item.user_has_permission = user_has_permission

    item_version = item.ordered_versions[0] if item.ordered_versions else None

    if item_version is None:
        if user_has_permission:
            return redirect("version_create", item_permalink)
        else:
            return redirect("home")

    item_screenshots = list(item.screenshots.all())

    item_reviews = []
    for version in item.ordered_versions:
        item_reviews.extend(version.reviews.all())

    for review in item_reviews:
        review.user_has_permission = review.has_permission(request.user)

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


def review_list(request):
    reviews = Review.objects.order_by("-created_at").prefetch_related(
        "version__item", "version", "user"
    )
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


def user_list(request):
    User = get_user_model()

    active_users = (
        User.objects.filter(Q(items_count__gt=0) | Q(reviews_count__gt=0))
        .annotate(total_contributions=F("items_count") + F("reviews_count"))
        .order_by("-total_contributions")
    )

    return render(request, "users.html", {"users": active_users})


def user_detail(request, username):
    User = get_user_model()
    show_user = get_object_or_404(User, username=username)
    items = get_filtered_items(request=request, user=show_user)
    user_has_permission = show_user.has_permission(request.user)

    if user_has_permission:
        items = get_filtered_items(request=request, items=Item.objects, user=show_user)

    reviews = (
        Review.objects.filter(user=show_user)
        .order_by("-created_at")
        .prefetch_related(
            "version",
            "version__item",
            "user",
        )
        .annotate(
            user_has_permission=Value(user_has_permission, output_field=BooleanField())
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


@login_required
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            item = form.save()
            return redirect("version_create", item_permalink=item.permalink)
    else:
        form = ItemForm()
    return render(request, "simple_form.html", {"form": form, "title": "Add Item"})


@login_required
def item_edit(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)

    if not item.has_permission(request.user):
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

    if not item.has_permission(request.user):
        return redirect("item_detail", item_permalink=item.permalink)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item deleted successfully")
        return redirect("home")

    return render(request, "item_confirm_delete.html", {"item": item})


def item_child_create(request, item_permalink, model_name, form_class):
    # Duplicate code for screenshots and versions
    item = get_object_or_404(Item, permalink=item_permalink)

    if not item.has_permission(request.user):
        messages.error(
            request, f"You do not have permission to add a {model_name} to this item."
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


def item_child_edit(
    request, model_class, item_permalink, model_name, form_class, child_id
):
    child = get_object_or_404(model_class, id=child_id)

    if not child.has_permission(request.user):
        messages.error(request, "You do not have permission to edit this item.")
        return redirect("item_detail", item_permalink=item_permalink)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, f"{model_name} updated.")
            return redirect("item_detail", item_permalink=item_permalink)
    else:
        form = form_class(instance=child)

    return render(
        request, "simple_form.html", {"form": form, "title": f"Edit {model_name}"}
    )


def item_child_delete(request, model_class, item_permalink, model_name, child_id):
    child = get_object_or_404(model_class, id=child_id)

    if not child.has_permission(request.user):
        messages.error(
            request, f"You do not have permission to delete this {model_name}."
        )
        return redirect("item_detail", item_permalink=item_permalink)

    if request.method == "POST":
        child.delete()
        messages.success(request, f"{model_name} deleted.")
        return redirect("item_detail", item_permalink=item_permalink)

    return render(
        request,
        "confirm_delete.html",
        {"object": child, "title": f"Delete {model_name}"},
    )


@login_required
def version_create(request, item_permalink):
    return item_child_create(request, item_permalink, "Version", VersionForm)


@login_required
def version_edit(request, item_permalink, version_id):
    return item_child_edit(
        request, Version, item_permalink, "Version", VersionForm, version_id
    )


@login_required
def review_create(request, item_permalink):
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


@login_required
def review_edit(request, item_permalink, review_id):
    return item_child_edit(request, Review, item_permalink, "Review", ReviewForm, review_id)


@login_required
def review_delete(request, item_permalink, review_id):
    return item_child_delete(request, Review, item_permalink, "Review", review_id)


@login_required
def screenshot_create(request, item_permalink):
    return item_child_create(request, item_permalink, "Screenshot", ScreenshotForm)


@login_required
def screenshot_edit(request, item_permalink, screenshot_id):
    return item_child_edit(
        request,
        Screenshot,
        item_permalink,
        "Screenshot",
        ScreenshotForm,
        screenshot_id,
    )


@login_required
def screenshot_delete(request, item_permalink, screenshot_id):
    return item_child_delete(request, Screenshot, item_permalink, "Screenshot", screenshot_id)


def download_create(request, item_permalink):
    item = get_object_or_404(Item, permalink=item_permalink)
    version = Version.objects.filter(item=item).order_by("-created_at").first()

    if version is None:
        messages.error(request, "No version available for download")
        return redirect("home")

    Version.objects.filter(id=version.id).update(
        downloads_count=F("downloads_count") + 1
    )
    Item.objects.filter(id=item.id).update(downloads_count=F("downloads_count") + 1)

    Download.objects.create(version=version, user=request.user)

    if version.file:
        return redirect(version.file.url)

    if version.link:
        return redirect(version.link)

    messages.error(request, "No file or URL found")
    return redirect("home")
