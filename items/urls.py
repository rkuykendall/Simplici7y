from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from .feeds import ItemsFeed, ReviewsFeed
from .views import (
    DownloadViewSet,
    ItemViewSet,
    ReviewViewSet,
    ScreenshotViewSet,
    TagViewSet,
    VersionViewSet,
    item_detail,
    items,
    login_view,
    log_out,
    reviews,
    settings,
    signup,
    user,
    users,
    view_404,
    tag,
    scenario,
    add_item,
    add_version,
    add_screenshot,
    version_edit,
    item_edit,
    item_delete,
    items_redirect,
    new_item_review, item_download,
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
    path("api/", include(router.urls)),
    path("items/<str:item_permalink>/", item_detail, name="item_detail"),
    path("items/", items_redirect, name="items_redirect"),
    path("scenarios/<str:item_permalink>/", scenario, name="scenario"),
    path("login/", login_view, name="login"),
    path("404/", view_404, name="view_404"),
    path("logout/", log_out, name="logout"),
    path("reviews/", reviews, name="reviews"),
    path("settings/", settings, name="settings"),
    path("signup/", signup, name="signup"),
    path("users/", users, name="users"),
    path("users/<str:username>/", user, name="user"),
    path("tags/<str:name>/", tag, name="tag"),
    path("items/new", add_item, name="add_item"),
    path("items/<str:item_permalink>/versions/new", add_version, name="add_version"),
    path(
        "items/<str:item_permalink>/screenshots/new",
        add_screenshot,
        name="add_screenshot",
    ),
    path(
        "items/<str:item_permalink>/versions/<str:version_id>/edit",
        version_edit,
        name="edit_version",
    ),
    path("items/<str:item_permalink>/edit", item_edit, name="item_edit"),
    path("items/<str:item_permalink>/delete", item_delete, name="item_delete"),
    path("items/<str:item_permalink>/downloads/new", item_download, name="item_download"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="simple_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="simple_form.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path(
        "items/<str:item_permalink>/reviews/new",
        new_item_review,
        name="new_item_review",
    ),
    path("items.rss", ItemsFeed()),
    path("reviews.rss", ReviewsFeed()),

]
