from django.core.management.base import BaseCommand
from django.db import transaction

from items.models import Item, Tag


class Command(BaseCommand):
    help = 'Cleans up used tags'

    @transaction.atomic
    def handle(self, *args, **options):
        # Combine "emfh" and "emfhs"
        self.combine_tags('emfh', 'emfhs')
        self.stdout.write(self.style.SUCCESS('Successfully combined "emfh" and "emfhs" tags'))

        self.combine_multiple_tags(['solo', 'single', 'singleplayer'])
        self.stdout.write(self.style.SUCCESS('Successfully combined "solo" and "single" and "singleplayer" tags'))

        self.combine_multiple_tags(['solocoop', 'coop', 'cooperative'])
        self.stdout.write(self.style.SUCCESS('Successfully combined "solocoop" and "coop" and "cooperative" tags'))

        # Remove "map" tag from any item with a "scenario" tag
        self.remove_map_from_scenario()
        self.stdout.write(self.style.SUCCESS('Successfully removed "map" tag from items with a "scenario" tag'))

        # Combine "map", "netmap", and "netmaps" tags
        self.combine_multiple_tags(['map', 'netmap', 'netmaps'])
        self.stdout.write(self.style.SUCCESS('Successfully combined "map", "netmap", and "netmaps" tags'))

    def combine_tags(self, tag1, tag2):
        tag1_obj = Tag.objects.get(name=tag1)
        tag2_obj = Tag.objects.get(name=tag2)

        # Get items associated with tag2
        items = Item.objects.filter(tags=tag2_obj)

        # Move items from tag2 to tag1 and update count if item wasn't already tagged with tag1
        for item in items:
            if tag1_obj not in item.tags.all():
                tag1_obj.count += 1
            item.tags.remove(tag2_obj)
            item.tags.add(tag1_obj)

        tag1_obj.save()

        tag2_obj.delete()

    def remove_map_from_scenario(self):
        scenario_tag = Tag.objects.get(name='scenario')
        map_tag = Tag.objects.get(name='map')

        # Get items with both tags
        items = Item.objects.filter(tags=scenario_tag).filter(tags=map_tag)
        for item in items:
            item.tags.remove(map_tag)

    def combine_multiple_tags(self, tags):
        target_tag_obj = Tag.objects.get(name=tags[0])

        # Loop through the rest of the tags
        for tag in tags[1:]:
            tag_obj = Tag.objects.get(name=tag)

            # Move items to the target tag and update the count
            items = Item.objects.filter(tags=tag_obj)
            for item in items:
                item.tags.remove(tag_obj)
                item.tags.add(target_tag_obj)

            target_tag_obj.count += tag_obj.count

            # Delete the tag
            tag_obj.delete()

        # Save the target tag
        target_tag_obj.save()
