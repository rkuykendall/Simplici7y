from django.db.models import F, Window, Min
from django.core.management.base import BaseCommand

from items.models import Review


class Command(BaseCommand):
    help = "Remove duplicate reviews"

    def handle(self, *args, **options):
        # Annotate reviews with duplicate_id
        reviews = Review.objects.annotate(
            duplicate_id=Window(
                expression=Min("id"),
                partition_by=["version", "user", "title", "body", "rating"],
            ),
        )

        review_ids_to_delete = list(
            reviews.exclude(id=F("duplicate_id")).values_list("pk", flat=True)
        )

        # Delete duplicate reviews
        Review.objects.filter(id__in=review_ids_to_delete).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {len(review_ids_to_delete)} duplicate reviews"
            )
        )
