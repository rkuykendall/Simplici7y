from django.db import models
from django.contrib.auth.models import User


def get_upload_path(instance, filename):
    model = instance.__class__.__name__.lower()
    return f'{model}/{instance.id}/{filename}'


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(max_length=255)
    permalink = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(TimeStampMixin):
    name = models.CharField(max_length=255)
    body = models.TextField()
    tc = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permalink = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class Version(TimeStampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.item} {self.name} by {self.item.user}"


class Download(TimeStampMixin):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)

    def __str__(self):
        if self.user is not None:
            return f"Download by {self.user.username} of version {self.version.name}"

        return f"Download of version {self.version.name}"


class Review(TimeStampMixin):
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Review by {self.user.username} - {self.title}"


class Screenshot(TimeStampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to=get_upload_path, null=True, blank=True)

    def __str__(self):
        return self.title
