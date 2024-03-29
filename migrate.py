import os
import re

import django
from datetime import datetime

from django.db import connections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s7.settings")
django.setup()

import sqlite3
from items.models import Item, Version, Download, Review, Screenshot, Tag, User
from django.contrib.auth import get_user_model
from django.utils import timezone
from contextlib import contextmanager


def has_field(model, field_name):
    if model is None:
        return False

    return field_name in [field.name for field in model._meta.get_fields()]


def correct_encoding(original_string):
    try:
        correct_string = original_string.encode("latin1").decode("utf8")
        # Strip out HTML tags
        correct_string = re.sub("<.*?>", "", correct_string)
        return correct_string
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        # If encoding or decoding fails, return the original string
        return original_string


def synchronize_last_sequence(model):
    # Postgresql aut-increments (called sequences) don't update the 'last_id' value if you manually specify an ID.
    # This sets the last incremented number to the last id
    sequence_name = model._meta.db_table + "_" + model._meta.pk.name + "_seq"
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT setval('"
            + sequence_name
            + "', (SELECT max("
            + model._meta.pk.name
            + ") FROM "
            + model._meta.db_table
            + "))"
        )
    print(
        "Last auto-incremental number for sequence " + sequence_name + " synchronized."
    )


@contextmanager
def suppress_auto_now(model, field_names):
    """
    From https://stackoverflow.com/a/59898220/519995
    idea taken here https://stackoverflow.com/a/35943149/1731460
    """
    fields_state = {}
    for field_name in [f for f in field_names if has_field(model, f)]:
        field = model._meta.get_field(field_name)
        fields_state[field] = {
            "auto_now": field.auto_now,
            "auto_now_add": field.auto_now_add,
        }

    for field in fields_state:
        field.auto_now = False
        field.auto_now_add = False
    try:
        yield
    finally:
        for field, state in fields_state.items():
            field.auto_now = state["auto_now"]
            field.auto_now_add = state["auto_now_add"]


User = get_user_model()

# Open a connection to your SQLite database
conn = sqlite3.connect("s7.db")

# Initialize a dictionary to track username frequencies
username_counts = {}

tables = [
    ("tags", Tag),
    ("taggings", None),
    ("users", User),
    ("items", Item),
    ("versions", Version),
    ("downloads", Download),
    ("reviews", Review),
    ("screenshots", Screenshot),
]

taggings_dict = {}
version_ids = set()
item_ids = set()
item_created_at = {}
user_ids = set()

# Clear all tables
for table, Model in tables[::-1]:
    if table == "items":
        Model.objects.update(tc=None)

    if Model is None:
        continue

    print(f"Deleting all {table} rows...")
    Model.objects.all().delete()


def clean_date(dt):
    if isinstance(dt, datetime):
        return dt

    if dt is None:
        return dt

    dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return timezone.make_aware(dt_obj)


# For each table in your SQLite database...
for table, Model in tables:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")

    column_names = [column[0] for column in cursor.description]

    instances = []  # Collect all instances for bulk creation

    for row in cursor.fetchall():
        row_dict = dict(zip(column_names, row))

        if table == "taggings":
            item_id = row_dict["taggable_id"]
            tag_id = row_dict["tag_id"]

            # Add item-tag relationship to dictionary
            if item_id in taggings_dict:
                taggings_dict[item_id].append(tag_id)
            else:
                taggings_dict[item_id] = [tag_id]

            continue

        if "tc_id" in row_dict and row_dict["tc_id"] == 0:
            row_dict["tc_id"] = None

        if table == "versions":
            if "body" in row_dict and row_dict["body"] is None:
                row_dict["body"] = ""

        if table == "downloads":
            row_dict.pop("item_id")

            # if version doesn't exist, skip the row
            version_id = row_dict.get("version_id")
            if version_id is None or version_id not in version_ids:
                continue

            # if user doesn't exist, nullify
            user_id = row_dict.get("user_id")
            if user_id is not None and user_id not in user_ids:
                print(f"Nullifying download for user_id {user_id}")
                row_dict["user_id"] = None

        if table == "users":
            # Map the fields
            created_at = clean_date(row_dict.pop("created_at", None))

            # If date_joined is not None, make it timezone-aware
            if created_at is not None:
                row_dict["date_joined"] = created_at

            row_dict["is_staff"] = row_dict.pop("admin", None) == 1
            row_dict["is_superuser"] = row_dict["is_staff"]
            row_dict["first_name"] = row_dict.pop("login", None)

            # If the username has been seen before, append a suffix to it
            username = row_dict.pop("permalink", None)
            count = username_counts.get(username, 0)
            if count > 0:
                username = f"{username}_{count}"
            username_counts[username] = count + 1
            row_dict["username"] = username

            # Remove unnecessary fields
            unnecessary_fields = [
                "crypted_password",
                "salt",
                "updated_at",
                "remember_token",
                "remember_token_expires_at",
            ]
            for field in unnecessary_fields:
                row_dict.pop(field, None)

        if table == "reviews":
            # Remove unnecessary fields
            unnecessary_fields = [
                "item_id",
                "relevancy",
            ]
            for field in unnecessary_fields:
                row_dict.pop(field, None)

            # Adjust review rating if it's outside the desired range
            rating = row_dict.get("rating")
            if rating is not None:
                row_dict["rating"] = max(1, min(5, rating))

            # if version doesn't exist, skip the row
            version_id = row_dict.get("version_id")
            if version_id is None or version_id not in version_ids:
                continue

        if table == "screenshots":
            if "title" in row_dict and row_dict["title"] is None:
                row_dict["title"] = ""

            # if item doesn't exist, skip the row
            item_id = row_dict.get("item_id")
            if item_id is None or item_id not in item_ids:
                print("SKIPPING ROW item_id", item_id, item_ids)
                print(row_dict)
                continue

        if "file" in row_dict and row_dict["file"] is not None:
            filename = row_dict["file"]
            row_dict["file"] = f"{table}/{row_dict['id']}/{filename}"

        if "updated_at" in row_dict:
            row_dict["updated_at"] = clean_date(row_dict["updated_at"])

        if "created_at" in row_dict:
            row_dict["created_at"] = clean_date(row_dict["created_at"])

        if "created_at" in row_dict and row_dict["created_at"] is None:
            row_dict["created_at"] = row_dict["updated_at"]

        if "updated_at" in row_dict and row_dict["updated_at"] is None:
            row_dict["updated_at"] = row_dict["created_at"]

        if (
            "created_at" in row_dict
            and row_dict["created_at"] is None
            and "updated_at" in row_dict
            and row_dict["updated_at"] is None
        ):
            # get item created_at
            item_id = row_dict.get("item_id")
            if item_id is not None and item_id in item_created_at:
                row_dict["created_at"] = item_created_at[item_id]
                row_dict["updated_at"] = item_created_at[item_id]
            else:
                # Downloads is full of junk data, so we don't care about it
                if table != "downloads":
                    print("Skipping record with no created_at or updated_at:")
                    print(row_dict)
                continue

        if "created_at" in row_dict:
            created_at = clean_date(row_dict["created_at"])
            updated_at = clean_date(row_dict.get("updated_at"))

            if created_at is not None and created_at > timezone.now():
                row_dict["created_at"] = updated_at

        if "body" in row_dict and row_dict["body"] is not None:
            row_dict["body"] = correct_encoding(
                row_dict["body"]
                .replace("\\r\\n", "\\r")
                .replace("\\r", "\r")
                .replace("\\n", "\n")
            )

        row_dict = {
            k: v
            for k, v in row_dict.items()
            if not (k.endswith("_count") or k.endswith("_created_at"))
        }
        print(row_dict)

        instance = Model(**row_dict)

        instances.append(instance)

        if len(instances) > 99999:
            with suppress_auto_now(Model, ["created_at", "updated_at"]):
                print(f"Saving {len(instances)} rows to {table} table...")
                Model.objects.bulk_create(instances)

            instances = []

    # Bulk create instances
    if Model is not None:
        with suppress_auto_now(Model, ["created_at", "updated_at"]):
            print(f"Saving {len(instances)} rows to {table} table...")
            Model.objects.bulk_create(instances)

    if table == "items":
        item_ids = set(Item.objects.values_list("id", flat=True))
        item_created_at = dict(
            Item.objects.values_list("id", "created_at").distinct().all()
        )

    if table == "versions":
        version_ids = set(Version.objects.values_list("id", flat=True))

    if table == "users":
        user_ids = set(User.objects.values_list("id", flat=True))

with suppress_auto_now(Item, ["created_at", "updated_at"]):
    tag_instances = []
    for item_id, tag_ids in taggings_dict.items():
        if item_id not in item_ids:
            print(f"Could not find item_id {item_id} in item_ids")
            continue

        item = Item.objects.get(id=item_id)
        tags = Tag.objects.filter(id__in=tag_ids)
        item.tags.set(tags)

    # Bulk create items
    print(f"Saving {len(tag_instances)} tags to tags table...")
    Tag.objects.bulk_create(tag_instances)


for table, Model in tables:
    if Model:
        synchronize_last_sequence(Model)

# Close the SQLite database connection
conn.close()
