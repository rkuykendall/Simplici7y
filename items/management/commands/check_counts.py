from django.core.management.base import BaseCommand
from django.db.models import (
    Count,
    Subquery,
    OuterRef,
    IntegerField,
    FloatField,
    Avg,
    ExpressionWrapper,
    F,
    Max,
    Q,
)
from django.db.models.functions import Coalesce

from items.models import Item, Download, Review, Screenshot, Version, Tag
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = "Check if download, review, screenshot, tag and user counts for each item are accurate"

    def handle(self, *args, **options):
        versions = Version.objects.all().annotate(
            new_downloads_count=Coalesce(
                Subquery(
                    Download.objects.filter(version=OuterRef("pk"))
                    .values("version")
                    .annotate(c=Count("id"))
                    .values("c"),
                    output_field=IntegerField(),
                ),
                0,
            ),
        )

        for version in versions:
            if version.new_downloads_count != version.downloads_count:
                self.stdout.write(
                    self.style.ERROR(
                        f"Version ID {version.pk} download count is incorrect. Calculated: {version.new_downloads_count}, Current: {version.downloads_count}"
                    )
                )

        # Check tag counts
        tags = (
            Item.tags.through.objects.all()
            .values("tag")
            .annotate(c=Count("item"))
            .values("tag", "c")
        )

        for tag in tags:
            current_tag = Tag.objects.get(id=tag["tag"])
            if current_tag.count != tag["c"]:
                self.stdout.write(
                    self.style.ERROR(
                        f"Tag ID {current_tag.id} count is incorrect. Calculated: {tag['c']}, Current: {current_tag.count}"
                    )
                )

        items = (
            Item.objects.all()
            .annotate(
                new_downloads_count=Coalesce(
                    Subquery(
                        Download.objects.filter(version__item=OuterRef("pk"))
                        .values("version__item")
                        .annotate(c=Count("id"))
                        .values("c"),
                        output_field=IntegerField(),
                    ),
                    0,
                ),
                new_reviews_count=Coalesce(
                    Subquery(
                        Review.objects.filter(version__item=OuterRef("pk"))
                        .values("version__item")
                        .annotate(c=Count("id"))
                        .values("c"),
                        output_field=IntegerField(),
                    ),
                    0,
                ),
                new_screenshots_count=Coalesce(
                    Subquery(
                        Screenshot.objects.filter(item=OuterRef("pk"))
                        .values("item")
                        .annotate(c=Count("id"))
                        .values("c"),
                        output_field=IntegerField(),
                    ),
                    0,
                ),
                new_rating_average=Coalesce(
                    Subquery(
                        Review.objects.filter(version__item=OuterRef("pk"))
                        .values("version__item")
                        .annotate(avg=Avg("rating"))
                        .values("avg"),
                        output_field=FloatField(),
                    ),
                    0.0,
                ),
            )
            .annotate(
                new_rating_weighted=ExpressionWrapper(
                    F("new_rating_average")
                    + (F("new_rating_average") - 2.5) * (F("new_reviews_count") / 10.0),
                    output_field=FloatField(),
                ),
                new_version_created_at=Coalesce(Max("versions__created_at"), None),
            )
        )

        for item in items:
            checks = {
                "downloads_count": item.new_downloads_count,
                "reviews_count": item.new_reviews_count,
                "screenshots_count": item.new_screenshots_count,
                "rating_average": item.new_rating_average,
                "rating_weighted": item.new_rating_weighted,
                "version_created_at": item.new_version_created_at,
            }

            for field, new_value in checks.items():
                if new_value != getattr(item, field):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Item ID {item.pk} {field} is incorrect. Calculated: {new_value}, Current: {getattr(item, field)}"
                        )
                    )

        # Check User items and reviews counts
        users = (
            User.objects.all()
            .annotate(
                new_items_count=Count("items", distinct=True),
                new_reviews_count=Count("reviews", distinct=True),
            )
            .filter(Q(new_items_count__gt=0) | Q(new_reviews_count__gt=0))
        )

        for user in users:
            checks = {
                "items_count": user.new_items_count,
                "reviews_count": user.new_reviews_count,
            }

            for field, new_value in checks.items():
                if new_value != getattr(user, field):
                    self.stdout.write(
                        self.style.ERROR(
                            f"User ID {user.pk} {field} is incorrect. Calculated: {new_value}, Current: {getattr(user, field)}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Finished checking counts"))
