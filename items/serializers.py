from rest_framework import serializers
from .models import Item, Version, Download, Review, Screenshot, Tag

read_only_fields = ["created_at", "updated_at"]


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = read_only_fields + ["user"]


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = "__all__"
        read_only_fields = read_only_fields


class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Download
        fields = "__all__"
        read_only_fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = read_only_fields + ["user"]


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = "__all__"
        read_only_fields = read_only_fields


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = "__all__"
