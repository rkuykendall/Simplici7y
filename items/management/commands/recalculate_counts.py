from django.core.management.base import BaseCommand
from django.db.models import Count, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce

from items.models import Item, Download, Review, Screenshot


class Command(BaseCommand):
    help = 'Recalculate download, review, and screenshot counts for each item'

    def handle(self, *args, **options):
        items = Item.objects.all().annotate(
            new_downloads_count=Coalesce(
                Subquery(
                    Download.objects.filter(version__item=OuterRef('pk')).values('version__item').annotate(c=Count('id')).values('c'),
                    output_field=IntegerField(),
                ), 0
            ),
            new_reviews_count=Coalesce(
                Subquery(
                    Review.objects.filter(version__item=OuterRef('pk')).values('version__item').annotate(c=Count('id')).values('c'),
                    output_field=IntegerField(),
                ), 0
            ),
            new_screenshots_count=Coalesce(
                Subquery(
                    Screenshot.objects.filter(item=OuterRef('pk')).values('item').annotate(c=Count('id')).values('c'),
                    output_field=IntegerField(),
                ), 0
            )
        )

        for item in items:
            Item.objects.filter(pk=item.pk).update(
                downloads_count=item.new_downloads_count,
                reviews_count=item.new_reviews_count,
                screenshots_count=item.new_screenshots_count
            )

        self.stdout.write(self.style.SUCCESS('Successfully recalculated counts'))
