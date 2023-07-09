from django.db.models import Value
from django.db.models.functions import Replace
from django.core.management.base import BaseCommand

from items.models import Review, Item, Version, Screenshot


class Command(BaseCommand):
    help = 'Replaces all instances of "" with " in all TextField fields'

    def handle(self, *args, **options):
        Item.objects.update(name=Replace("name", Value('""'), Value('"')))
        Item.objects.update(body=Replace("body", Value('""'), Value('"')))

        Version.objects.update(name=Replace("name", Value('""'), Value('"')))
        Version.objects.update(body=Replace("body", Value('""'), Value('"')))

        Review.objects.update(title=Replace("title", Value('""'), Value('"')))
        Review.objects.update(body=Replace("body", Value('""'), Value('"')))

        Screenshot.objects.update(title=Replace("title", Value('""'), Value('"')))

        self.stdout.write(self.style.SUCCESS('Successfully replaced "" with "'))
