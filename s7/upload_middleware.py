from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class LargeFileUploadMiddleware(MiddlewareMixin):
    """
    Middleware to optimize handling of large file uploads.
    """

    def process_request(self, request):
        """
        Configure upload handlers for large files.
        """
        if (
            request.method == "POST"
            and request.content_type
            and "multipart/form-data" in request.content_type
        ):
            # Get content length
            content_length = request.META.get("CONTENT_LENGTH")
            if content_length:
                try:
                    content_length = int(content_length)
                    # If upload is larger than 10MB, use only temporary file handler
                    if content_length > 10 * 1024 * 1024:
                        request.upload_handlers = [
                            "s7.upload_handlers.ChunkedTemporaryFileUploadHandler",
                            "django.core.files.uploadhandler.TemporaryFileUploadHandler",
                        ]
                        logger.info(
                            f"Large file upload detected: {content_length} bytes"
                        )
                except (ValueError, TypeError):
                    pass

        return None

    def process_response(self, request, response):
        """
        Clean up any temporary upload progress data.
        """
        if hasattr(request, "upload_handlers"):
            # Clean up progress tracking if it exists
            progress_id = request.GET.get("progress_id")
            if progress_id:
                from django.core.cache import cache

                cache.delete(f"upload_progress_{progress_id}")

        return response
