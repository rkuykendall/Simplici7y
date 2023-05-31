from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    ItemViewSet,
    VersionViewSet,
    DownloadViewSet,
    ReviewViewSet,
    ScreenshotViewSet,
    TagViewSet,
    items,
    item_detail,
    reviews,
    users,
    submit,
    settings,
    logout_view,
    about,
    signup,
    login_view,
    user,
)

router = DefaultRouter()
router.register(r"items", ItemViewSet)
router.register(r"versions", VersionViewSet)
router.register(r"downloads", DownloadViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"screenshots", ScreenshotViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    path("", items, name="home"),
    path("about/", about, name="about"),
    path("api/", include(router.urls)),
    path("items/", items, name="items"),
    path("items/<str:item_permalink>/", item_detail, name="item_detail"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("reviews/", reviews, name="reviews"),
    path("settings/", settings, name="settings"),
    path("signup/", signup, name="signup"),
    path("submit/", submit, name="submit"),
    path("users/", users, name="users"),
    path("users/<str:username>/", user, name="user"),
]
