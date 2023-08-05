import discord
import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading

from s7 import settings
from .models import Version, Review


def send_discord_message(channel_id, content):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def send():
            intents = discord.Intents.default()
            client = discord.Client(intents=intents)

            @client.event
            async def on_ready():
                await client.wait_until_ready()
                channel = await client.fetch_channel(channel_id)
                if channel:
                    response = await channel.send(content)
                    await response.publish()

                await client.close()

            await client.start(settings.DISCORD_BOT_TOKEN)

        loop.run_until_complete(send())

    thread = threading.Thread(target=run)
    thread.start()


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
    send_discord_message(channel_id, content)
