from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify


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
    permalink = models.SlugField(max_length=255, unique=True)
    tags = models.ManyToManyField(Tag)

    # class Meta:
    #     ordering = ['version_created_at']

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.permalink = slugify(self.name)
    #     super().save(*args, **kwargs)

    def find_version(self):
        return Version.objects.filter(item=self).latest('created_at')

    def rand_screenshot(self):
        return Screenshot.objects.order_by('?').first()

    def get_absolute_url(self):
        reverse('item_detail', args={'permalink': self.permalink})


class Version(TimeStampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.item} {self.name} by {self.item.user}"

    def download_button(self):
        if self.file:
            url = '<a href="{}" class="button down">Download</a>'.format(self.item.get_absolute_url())
        elif self.link:
            url = '<a href="{}" class="button next" target="_blank">Webpage</a>'.format(self.item.get_absolute_url())
        else:
            url = ""

        return mark_safe('<div class="sidenote">{}</div>'.format(url))


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
