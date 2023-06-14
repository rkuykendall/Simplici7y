from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef, Count

from items.models import Item
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = "Remove orphaned items and users"

    def handle(self, *args, **options):
        Item.objects.filter(
            ~Exists(Item.objects.filter(tc_id=OuterRef('pk')))
        ).filter(version__isnull=True).delete()

        User.objects.annotate(
            downloads_count=Count('downloads')
        ).filter(items_count=0, reviews_count=0, downloads_count=0).delete()

        self.stdout.write(self.style.SUCCESS("Successfully removed orphaned items and users"))
