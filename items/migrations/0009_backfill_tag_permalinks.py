from django.db import migrations, models
from django.utils.text import slugify


def populate_permalink(apps, schema_editor):
    Tag = apps.get_model("items", "Tag")
    tags_without_permalink = Tag.objects.filter(permalink__exact="")

    for tag in tags_without_permalink:
        tag.permalink = slugify(tag.name)
        tag.save(update_fields=["permalink"])


class Migration(migrations.Migration):
    dependencies = [
        ("items", "0008_alter_version_name"),
    ]

    operations = [
        migrations.RunPython(populate_permalink),
    ]
