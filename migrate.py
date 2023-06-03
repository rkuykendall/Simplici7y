import os
import django
from datetime import datetime

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
    # ("downloads", Download),
    ("reviews", Review),
    ("screenshots", Screenshot),
]

taggings_dict = {}
version_ids = set()
item_ids = set()
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

            # if version doesn't exist, skip the row
            version_id = row_dict.get("version_id")
            if version_id is None or version_id not in version_ids:
                print("SKIPPING ROW version_id", version_id, version_ids)
                print(row_dict)
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

        if "file" in row_dict and row_dict['file'] is not None:
            filename = row_dict['file']
            row_dict['file'] = f"{table}/{row_dict['id']}/{filename}"

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
            print("Skipping record with no created_at or updated_at")
            continue

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

    if table == "versions":
        version_ids = set(Version.objects.values_list("id", flat=True))

    if table == "users":
        user_ids = set(User.objects.values_list("id", flat=True))


with suppress_auto_now(Item, ["created_at", "updated_at"]):
    # Iterate over every item id in the taggings_dict
    for item_id in taggings_dict:
        if item_id not in item_ids:
            print(f"Could not find item_id {item_id} in item_ids")
            continue

        # Fetch the item object for this item_id
        item = Item.objects.get(id=item_id)
        # Get tag ids for this item from taggings_dict
        tag_ids = taggings_dict.get(item_id, [])
        # Fetch Tag instances
        tags = Tag.objects.filter(id__in=tag_ids)
        # Save tags to the item
        item.tags.set(tags)
        # Save the item
        item.save()


# Close the SQLite database connection
conn.close()
