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
    item_list,
    session_create,
    log_out,
    review_list,
    settings,
    signup,
    user_detail,
    user_list,
    tag_detail,
    scenario_detail,
    item_create,
    version_create,
    screenshot_create,
    version_edit,
    item_edit,
    item_delete,
    items_list_redirect,
    review_create,
    download_create,
    tag_list,
    screenshot_edit,
    screenshot_delete,
    review_edit,
    review_delete,
)

router = DefaultRouter()
router.register(r"items", ItemViewSet)
router.register(r"versions", VersionViewSet)
router.register(r"downloads", DownloadViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"screenshots", ScreenshotViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    path("", item_list, name="home"),
    path("api/", include(router.urls)),
    path("items/<str:item_permalink>/", item_detail, name="item_detail"),
    path("items/", items_list_redirect, name="items_redirect"),
    path("scenarios/<str:item_permalink>/", scenario_detail, name="scenario"),
    path("login/", session_create, name="login"),
    path("logout/", log_out, name="logout"),
    path("reviews/", review_list, name="reviews"),
    path("settings/", settings, name="settings"),
    path("signup/", signup, name="signup"),
    path("users/", user_list, name="users"),
    path("users/<str:username>/", user_detail, name="user"),
    path("tags/", tag_list, name="tags"),
    path("tags/<str:name>/", tag_detail, name="tag"),
    path("items/new", item_create, name="item_create"),
    path(
        "items/<str:item_permalink>/versions/new", version_create, name="version_create"
    ),
    path(
        "items/<str:item_permalink>/screenshots/new",
        screenshot_create,
        name="add_screenshot",
    ),
    path(
        "items/<str:item_permalink>/screenshots/<str:screenshot_id>/edit",
        screenshot_edit,
        name="screenshot_edit",
    ),
    path(
        "items/<str:item_permalink>/screenshots/<str:screenshot_id>/delete",
        screenshot_delete,
        name="screenshot_delete",
    ),
    path(
        "items/<str:item_permalink>/versions/<str:version_id>/edit",
        version_edit,
        name="edit_version",
    ),
    path("items/<str:item_permalink>/edit", item_edit, name="item_edit"),
    path("items/<str:item_permalink>/delete", item_delete, name="item_delete"),
    path(
        "items/<str:item_permalink>/downloads/new",
        download_create,
        name="item_download",
    ),
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
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "items/<str:item_permalink>/reviews/new",
        review_create,
        name="new_item_review",
    ),
    path(
        "items/<str:item_permalink>/reviews/<str:review_id>/edit",
        review_edit,
        name="review_edit",
    ),
    path(
        "items/<str:item_permalink>/reviews/<str:review_id>/delete",
        review_delete,
        name="review_delete",
    ),
    path("items.rss", ItemsFeed()),
    path("reviews.rss", ReviewsFeed()),
]
