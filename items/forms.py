import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Count

from items.models import Item, Version, Screenshot, Review, Tag

User = get_user_model()


MARKDOWN_LINK = 'Formatted with <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">Markdown</a>.'


def validate_passphrase(value):
    if value != "escapewillmakemegod":
        raise ValidationError(
            "Incorrect passphrase.",
            params={"value": value},
        )


class UserForm(BaseUserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    passphrase = forms.CharField(
        label="Passphrase",
        help_text='Ask on the <a href="https://discord.gg/ZuJRd8xJ">Discord</a> for the passphrase.',
        validators=[validate_passphrase],
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "email",
            "password1",
            "password2",
            "passphrase",
        )
        labels = {
            "first_name": "Display name",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove passphrase field when editing an existing user
        if self.instance and self.instance.pk:
            self.fields.pop("passphrase")

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]

        if not user.first_name:
            user.first_name = self.cleaned_data["username"]

        if commit:
            user.save()
        return user


popular_tag_names = [
    "multiplayer",
    "netmaps",
    "scenario",
    "solo",
    "solocoop",
    "survival",
    "enhancement",
    "emfh",
    "ctf",
    "koth",
    "ktmwtb",
    "plugin",
    "lua",
    "physics",
    "script",
    "utility",
]


class ItemForm(forms.ModelForm):
    popular_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(name__in=popular_tag_names).order_by("-count"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    additional_tags = forms.CharField(
        max_length=255,
        required=False,
        help_text="Enter additional tags separated by commas or spaces.",
    )

    tc_radio_choice = forms.ChoiceField(
        widget=forms.RadioSelect,
        required=False,
        label="Marathon game",
    )

    class Meta:
        model = Item
        fields = (
            "name",
            "byline",
            "body",
            "tc_radio_choice",
            "tc",
            "popular_tags",
            "additional_tags",
        )
        labels = {
            "tc": "Total conversion",
        }
        help_texts = {
            "tc": "Only for uploads not for the original trilogy. This will override the field above.",
            "body": MARKDOWN_LINK,
            "byline": "Optional. Will be displayed instead of username if provided.",
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        try:
            marathon = Item.objects.get(permalink="marathon")
            marathon_2 = Item.objects.get(permalink="marathon-2-durandal")
            marathon_infinity = Item.objects.get(permalink="marathon-infinity")
            self.fields["tc_radio_choice"].choices = [
                (marathon.pk, "Marathon"),
                (marathon_2.pk, "Marathon 2: Durandal"),
                (marathon_infinity.pk, "Marathon Infinity"),
            ]
        except Item.DoesNotExist:
            print("Marathon trilogy not found. Skipping tc_radio_choice.")
            pass

        try:
            scenario_tag = Tag.objects.get(name="scenario")
            self.fields["tc"].queryset = Item.objects.filter(tags=scenario_tag)
        except Tag.DoesNotExist:
            print("Scenario tag not found. Skipping tc field.")
            pass

        if self.instance and self.instance.pk:
            self.fields["popular_tags"].initial = self.instance.tags.filter(
                name__in=popular_tag_names
            )
            self.fields["additional_tags"].initial = ", ".join(
                tag.name
                for tag in self.instance.tags.exclude(name__in=popular_tag_names)
            )

    def clean_additional_tags(self):
        data = self.cleaned_data["additional_tags"]
        # split by commas or spaces
        tag_list = re.findall(r"[\w-]+", data)
        return tag_list

    from django.db.models import Count

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.tc is None and self.cleaned_data["tc_radio_choice"]:
            instance.tc = Item.objects.get(pk=self.cleaned_data["tc_radio_choice"])

        # Get the current tags before clearing them
        previous_tags = set(instance.tags.values_list("pk", flat=True))

        # Clear all existing tags before adding new ones.
        instance.tags.clear()

        # add popular tags
        for tag in self.cleaned_data["popular_tags"]:
            instance.tags.add(tag)

        # create and add additional tags
        for tag_name in self.cleaned_data["additional_tags"]:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

        # Update all_tags set with the new tags
        all_tags = previous_tags
        all_tags.update(set(instance.tags.values_list("pk", flat=True)))

        instance.save()

        # Update the count for all affected tags
        tags = (
            Tag.objects.filter(pk__in=all_tags)
            .annotate(c=Count("item"))
            .values("pk", "c")
        )

        for tag in tags:
            Tag.objects.filter(pk=tag["pk"]).update(count=tag["c"])

        return instance


class VersionForm(forms.ModelForm):
    link = forms.CharField(
        required=False,
        validators=[URLValidator()],
        help_text="Only required if no file is uploaded.",
    )

    class Meta:
        model = Version
        fields = ("name", "body", "file", "link")
        labels = {
            "name": "Version number",
            "body": "Release notes or changelog",
        }
        help_texts = {
            "body": "Optional. " + MARKDOWN_LINK,
        }

    def clean(self):
        cleaned_data = super().clean()
        link = cleaned_data.get("link")
        file = cleaned_data.get("file")

        if not link and not file:
            raise forms.ValidationError(
                "At least one of Link or File must be provided."
            )


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshot
        fields = ("title", "file", "order")
        help_texts = {
            "title": "Optional.",
            "order": "Screenshots are displayed in ascending order, then by first created.",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("title", "rating", "body")
        help_texts = {
            "body": MARKDOWN_LINK,
        }

    rating = forms.IntegerField(min_value=1, max_value=5, help_text="1-5 Stars")
