from django.core.management.base import BaseCommand
from items.models import Item


class Command(BaseCommand):
    help = 'Prints the URLs of Items with specified tags'

    def handle(self, *args, **options):
        tag_names = ["emfh", "koth", "ktmwtb"]
        excluded_tag_names = ["netmaps", "physics", "music", "script", "plugin", "utility", "solocoop", "solo", "halo"]
        # Get all items with any of the tags in tag_names but not with excluded_tag_names
        items = Item.objects.filter(
            tags__name__in=tag_names
        ).exclude(
            tags__name__in=excluded_tag_names
        ).order_by("-downloads_count").distinct()

        for item in items:
            self.stdout.write(self.style.SUCCESS("https://simplici7y.com" + item.get_absolute_url()))
