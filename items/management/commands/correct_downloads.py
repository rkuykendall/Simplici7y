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
                        insert_sql = "INSERT INTO items_downloads (version_id) VALUES (%s)"
                        cursor.executemany(insert_sql, [(default_version.id,)] * discrepancy)
                        self.stdout.write(f'Corrected download count for item {item.id}')
