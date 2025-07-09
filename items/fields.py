from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io
import uuid
import os
import threading
import logging

logger = logging.getLogger(__name__)


def process_image_async(screenshot_id, image_path):
    """
    Process image thumbnails asynchronously to avoid blocking the upload.
    """

    def _process():
        try:
            from items.models import Screenshot

            screenshot = Screenshot.objects.get(id=screenshot_id)

            # Generate thumbnail
            if screenshot.file:
                with screenshot.file.open("rb") as f:
                    image = Image.open(f)

                    # Create thumbnail (300x400)
                    image.thumbnail((300, 400), Image.Resampling.LANCZOS)
                    thumb_io = io.BytesIO()
                    image.save(thumb_io, format="JPEG", quality=90)
                    thumb_io.seek(0)

                    # Save thumbnail
                    thumb_name = f"thumb_{uuid.uuid4()}.jpg"
                    thumb_path = os.path.join(os.path.dirname(image_path), thumb_name)
                    default_storage.save(thumb_path, ContentFile(thumb_io.read()))

                    # Update screenshot record
                    screenshot.thumbnail_path = thumb_path
                    screenshot.save(update_fields=["thumbnail_path"])

                    logger.info(f"Processed thumbnail for screenshot {screenshot_id}")

        except Exception as e:
            logger.error(f"Error processing image {screenshot_id}: {e}")

    # Start processing in background thread
    thread = threading.Thread(target=_process)
    thread.daemon = True
    thread.start()


class OptimizedFileField(models.FileField):
    """
    Custom FileField that handles large file uploads more efficiently.
    """

    def save_form_data(self, instance, data):
        """
        Save uploaded file data efficiently.
        """
        if data is not None:
            # Save the file immediately but defer processing
            super().save_form_data(instance, data)

            # If this is a screenshot, process thumbnails async
            if (
                hasattr(instance, "file")
                and instance.__class__.__name__ == "Screenshot"
            ):
                if hasattr(instance, "pk") and instance.pk:
                    process_image_async(instance.pk, instance.file.path)
