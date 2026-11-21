from django.urls import path


def boom(request):
    raise RuntimeError("boom")


urlpatterns = [path("boom/", boom)]
