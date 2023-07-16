from django.core.management.base import BaseCommand
from django.db import transaction

from items.models import Item, Download

class Command(BaseCommand):
    help = 'Corrects the downloads count for each item'

    @transaction.atomic
    def handle(self, *args, **options):
        for item in Item.objects.all():
            actual_downloads_count = 0
            for version in item.versions.all():
                actual_downloads_count += version.downloads.count()
            discrepancy = item.downloads_count - actual_downloads_count
            if discrepancy > 0:
                default_version = item.versions.order_by("-created_at").first()
                if default_version:
                    for _ in range(discrepancy):
                        Download.objects.create(user=None, version=default_version)
                    self.stdout.write(f'Corrected download count for item {item}')
