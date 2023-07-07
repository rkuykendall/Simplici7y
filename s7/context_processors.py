from django.conf import settings


def from_settings(request):
    return settings.TEMPLATE_VALUES
