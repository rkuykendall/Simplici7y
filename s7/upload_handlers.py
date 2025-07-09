from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
import os
import tempfile


class ChunkedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """
    Custom upload handler that efficiently handles large files by using
    temporary files and chunked processing to avoid memory issues.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = None

    def new_file(self, *args, **kwargs):
        """
        Create a new temporary file for the upload.
        """
        super().new_file(*args, **kwargs)
        if self.content_length > (5 * 1024 * 1024):  # 5MB threshold
            # Create a temporary file in the system temp directory
            self.file = tempfile.NamedTemporaryFile(
                suffix=".upload",
                dir=getattr(settings, "FILE_UPLOAD_TEMP_DIR", None),
                delete=False,
            )

    def receive_data_chunk(self, raw_data, start):
        """
        Receive data chunks and write directly to temp file.
        """
        if self.file:
            self.file.write(raw_data)
        else:
            return super().receive_data_chunk(raw_data, start)

    def file_complete(self, file_size):
        """
        Complete the file upload and return the uploaded file.
        """
        if self.file:
            self.file.seek(0)
            return TemporaryUploadedFile(
                name=self.file_name,
                content_type=self.content_type,
                size=file_size,
                charset=self.charset,
                content_type_extra=self.content_type_extra,
            )
        else:
            return super().file_complete(file_size)


class ProgressFileUploadHandler(TemporaryFileUploadHandler):
    """
    Upload handler that tracks progress for large files.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.progress_id = None
        if request:
            self.progress_id = request.GET.get("progress_id")

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        if self.progress_id:
            # Store initial progress in cache/session
            from django.core.cache import cache

            cache.set(
                f"upload_progress_{self.progress_id}",
                {"uploaded": 0, "total": self.content_length, "percent": 0},
                3600,
            )  # 1 hour timeout

    def receive_data_chunk(self, raw_data, start):
        if self.progress_id:
            from django.core.cache import cache

            progress = cache.get(f"upload_progress_{self.progress_id}", {})
            progress["uploaded"] = start + len(raw_data)
            progress["percent"] = int(
                (progress["uploaded"] / self.content_length) * 100
            )
            cache.set(f"upload_progress_{self.progress_id}", progress, 3600)

        return super().receive_data_chunk(raw_data, start)
