from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Item, Tag


@receiver(m2m_changed, sender=Item.tags.through)
def update_tag_count(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for tag in Tag.objects.filter(pk__in=pk_set):
            tag.count += 1
            tag.save()
    elif action == "post_remove":
        for tag in Tag.objects.filter(pk__in=pk_set):
            tag.count -= 1
            tag.save()
