import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.exceptions import ValidationError

from items.models import Item, Version, Screenshot, Review, Tag

User = get_user_model()


def validate_passphrase(value):
    if value != 'escapewillmakemegod':
        raise ValidationError(
            "Incorrect passphrase.",
            params={"value": value},
        )


class UserForm(BaseUserCreationForm):
    email = forms.EmailField(required=True)
    passphrase = forms.CharField(
        label="Passphrase",
        help_text="Ask on the <a href=\"https://discord.gg/ZuJRd8xJ\">Discord</a> for the passphrase.",
        validators=[validate_passphrase],
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2", "passphrase")
        labels = {
            "first_name": "Display name",
        }

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]

        if not user.first_name:
            user.first_name = self.cleaned_data["username"]

        if commit:
            user.save()
        return user


class ItemForm(forms.ModelForm):
    popular_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(name__in=[
            'ctf', 'emfh', 'enhancement', 'koth', 'ktmwtb', 'lua', 'map', 'multiplayer',
            'physics', 'plugin', 'scenario', 'script', 'solo', 'solocoop', 'survival', 'utility'
        ]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    additional_tags = forms.CharField(
        max_length=255,
        required=False,
        help_text="Enter additional tags separated by commas or spaces."
    )

    class Meta:
        model = Item
        fields = ("name", "body", "tc", "popular_tags", "additional_tags")
        labels = {
            "tc": "Total conversion",
        }
        help_texts = {
            "tc": "If n/a leave blank",
            "body": "Formatted with <a href=\"https://www.markdownguide.org/cheat-sheet/\" target=\"_blank\">Markdown</a>."
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        scenario_tag = Tag.objects.get(name='scenario')
        self.fields['tc'].queryset = Item.objects.filter(tags=scenario_tag)

        if self.instance and self.instance.pk:
            self.fields['popular_tags'].initial = self.instance.tags.filter(
                name__in=[
                    'ctf', 'emfh', 'enhancement', 'koth', 'ktmwtb', 'lua', 'map', 'multiplayer',
                    'physics', 'plugin', 'scenario', 'script', 'solo', 'solocoop', 'survival', 'utility'
                ]
            )
            self.fields['additional_tags'].initial = ", ".join(
                tag.name for tag in self.instance.tags.exclude(
                    name__in=[
                        'ctf', 'emfh', 'enhancement', 'koth', 'ktmwtb', 'lua', 'map', 'multiplayer',
                        'physics', 'plugin', 'scenario', 'script', 'solo', 'solocoop', 'survival', 'utility'
                    ]
                )
            )

    def clean_additional_tags(self):
        data = self.cleaned_data['additional_tags']
        # split by commas or spaces
        tag_list = re.findall(r'[\w-]+', data)
        return tag_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

            # Clear all existing tags before adding new ones.
            # This allows removing tags from the Item during edit.
            instance.tags.clear()

            # add popular tags
            for tag in self.cleaned_data['popular_tags']:
                instance.tags.add(tag)

            # create and add additional tags
            for tag_name in self.cleaned_data['additional_tags']:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)

            # Only save instance if there are tags to avoid unnecessary database writes.
            if self.cleaned_data['popular_tags'] or self.cleaned_data['additional_tags']:
                instance.save()

        return instance


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ("name", "body", "file", "link")


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshot
        fields = ("title", "file")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("title", "rating", "body")

    rating = forms.IntegerField(min_value=1, max_value=5)
