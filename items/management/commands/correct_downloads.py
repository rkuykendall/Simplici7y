from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction, connection

from items.models import Item, Version

class Command(BaseCommand):
    help = 'Corrects the downloads count for each item'

    @transaction.atomic  # This will ensure all database operations in this function are done as a single transaction
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for item in Item.objects.all():
                actual_downloads_count = 0
                for version in item.versions.all():
                    actual_downloads_count += version.downloads.count()
                discrepancy = item.downloads_count - actual_downloads_count
                if discrepancy > 0:
                    default_version = item.versions.order_by("-created_at").first()
                    if default_version:
                        insert_sql = "INSERT INTO items_download (version_id, created_at, updated_at) VALUES (%s, %s, %s)"
                        params = [(default_version.id, timezone.now(), timezone.now()) for _ in range(discrepancy)]
                        cursor.executemany(insert_sql, params)
                        self.stdout.write(f'Corrected download count for item {item.id}')
