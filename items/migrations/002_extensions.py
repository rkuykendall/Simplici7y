from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension, TrigramExtension


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("items", "0001_initial"),
    ]

    operations = [
        UnaccentExtension(),
        TrigramExtension(),
    ]
