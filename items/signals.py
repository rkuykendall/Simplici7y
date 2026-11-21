import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Version, Review

logger = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"
TIMEOUT_SECONDS = 10


def discord_request(path, payload=None):
    request = urllib.request.Request(
        DISCORD_API + path,
        data=json.dumps(payload or {}).encode(),
        method="POST",
        headers={
            "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://simplici7y.com, 1.0)",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


def post_announcement(channel_id, content):
    """Post to an announcement channel and publish it to following servers."""
    try:
        message = discord_request(
            f"/channels/{channel_id}/messages", {"content": content}
        )
        discord_request(f"/channels/{channel_id}/messages/{message['id']}/crosspost")
    except Exception:
        logger.exception("Discord post to channel %s failed: %s", channel_id, content)


def send_discord_message(channel_id, content):
    # Off the request thread, so a slow Discord never delays the page.
    threading.Thread(target=post_announcement, args=(channel_id, content)).start()


@receiver(post_save, sender=Version)
@receiver(post_save, sender=Review)
def notify_discord(sender, instance, created, **kwargs):
    if not created or not settings.DISCORD_BOT_TOKEN:
        return

    channel_id = (
        settings.DISCORD_UPLOADS_CHANNEL_ID
        if sender == Version
        else settings.DISCORD_REVIEWS_CHANNEL_ID
    )

    if not channel_id:
        return

    content = f"{settings.CANONICAL_DOMAIN}{instance.get_absolute_url()}"
    # Only announce once the upload or review is actually saved.
    transaction.on_commit(lambda: send_discord_message(channel_id, content))
