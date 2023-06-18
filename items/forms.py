from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.exceptions import ValidationError

from items.models import Item, Version, Screenshot, Review

User = get_user_model()


def validate_passphrase(value):
    if value != 'test':
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
    class Meta:
        model = Item
        fields = ("name", "body", "tc")  # , "tags")
        labels = {
            "tc": "Total conversion",
        }
        help_texts = {
            "tc": "if n/a leave blank",
        }


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
