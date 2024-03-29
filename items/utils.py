from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.core.paginator import Paginator
from django.db.models import (
    Prefetch,
    Q,
    Count,
    BooleanField,
    Value,
    When,
    Case,
)
from django.db.models.functions import Length

from .models import Item, Version, Screenshot

PAGE_SIZE = 20


def order_items(items, order):
    if order == "old":
        items = items.order_by("version_created_at")
    elif order == "reviews":
        items = items.filter(reviews_count__gt=0).order_by(
            "-rating_average", "-reviews_count", "-version_created_at"
        )
    elif order == "best":
        items = items.filter(reviews_count__gt=0).order_by(
            "-rating_weighted",
            "-rating_average",
            "-reviews_count",
            "-version_created_at",
        )
    elif order == "worst":
        items = items.filter(reviews_count__gt=0).order_by(
            "rating_weighted", "rating_average", "-reviews_count", "-version_created_at"
        )
    elif order == "loud":
        items = items.filter(reviews_count__gt=0).order_by(
            "-reviews_count", "-version_created_at"
        )
    elif order == "popular":
        items = items.order_by("-downloads_count", "-version_created_at")
    elif order == "random":
        items = items.order_by("?")
    else:
        # default to new
        items = items.order_by("-version_created_at")

    return items


def get_filtered_items(
    request=None, items=None, tc=None, tag=None, user=None, scenarios=False
):
    items = items or Item.objects.exclude(version_created_at__isnull=True)

    if tc:
        items = items.filter(tc=tc)

    if tag:
        items = items.filter(tags=tag)

    if user:
        items = items.filter(user=user)

    MAX_DESCRIPTION_LENGTH = 2000

    items = items.annotate(
        body_length=Length("body"),
        should_truncate=Case(
            When(body_length__gt=MAX_DESCRIPTION_LENGTH, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    )

    latest_version = Prefetch(
        "versions",
        queryset=Version.objects.order_by("-created_at"),
        to_attr="latest_version",
    )

    random_screenshots = Prefetch(
        "screenshots",
        queryset=Screenshot.objects.order_by("order", "?"),
        to_attr="random_screenshot",
    )

    items = items.prefetch_related(latest_version, random_screenshots, "user")

    order = request.GET.get("order", None) if request else None
    search = request.GET.get("search", None) if request else None
    page_number = request.GET.get("page") if request else None

    if search:
        vector = (
            SearchVector("name", weight="A")
            + SearchVector("byline", weight="A")
            + SearchVector("tags_names", weight="D")
            + SearchVector("body", weight="D")
        )
        query = SearchQuery(search)

        items = (
            items.annotate(
                tags_names=ArrayAgg(
                    "tags__name",
                    distinct=True,
                )
            )
            .annotate(rank=SearchRank(vector, query))
            .filter(rank__gte=0.02)
            .order_by("-rank", "-version_created_at")
            .distinct()
        )
    else:
        items = order_items(items, order)

    if request:
        items = items.annotate(user_has_permission=Q(user_id=request.user.id))

    items = items.annotate(scenario_items_count=Count("items"))
    if scenarios:
        items = items.filter(scenario_items_count__gt=1).order_by(
            "-scenario_items_count"
        )

    paginator = Paginator(items, PAGE_SIZE)

    page_obj = paginator.get_page(page_number)

    return page_obj


def page_out_of_bounds(request, page_obj):
    page_number = request.GET.get("page")
    if page_number:
        try:
            page_number = int(page_number)
        except ValueError:
            return True
        else:
            return page_obj.number != page_number
    return False
