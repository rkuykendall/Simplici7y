from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.contrib.auth import get_user_model
from items.models import Item
import time
import os


class Command(BaseCommand):
    help = "Test file upload performance"

    def add_arguments(self, parser):
        parser.add_argument("--file-size", type=int, default=10, help="File size in MB")
        parser.add_argument(
            "--username", type=str, default="test", help="Username for testing"
        )

    def handle(self, *args, **options):
        User = get_user_model()
        file_size_mb = options["file_size"]
        username = options["username"]

        # Create test user if not exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "Test User", "email": "test@example.com"},
        )

        # Create test item
        item = Item.objects.create(
            name=f"Test Upload {int(time.time())}",
            user=user,
            body="Test upload for performance testing",
        )

        self.stdout.write(f"Created test item: {item.name}")

        # Generate test file data
        file_size_bytes = file_size_mb * 1024 * 1024
        test_data = b"0" * file_size_bytes

        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            f"test_file_{file_size_mb}mb.txt", test_data, content_type="text/plain"
        )

        # Test upload timing
        client = Client()
        client.force_login(user)

        start_time = time.time()

        response = client.post(
            f"/items/{item.permalink}/versions/new",
            {
                "name": f"Test Version {int(time.time())}",
                "body": "Test version for performance testing",
                "file": uploaded_file,
            },
        )

        end_time = time.time()
        upload_time = end_time - start_time

        if response.status_code == 302:  # Redirect on success
            self.stdout.write(
                self.style.SUCCESS(
                    f"Upload successful! {file_size_mb}MB uploaded in {upload_time:.2f} seconds"
                )
            )

            # Calculate speed
            speed_mbps = (file_size_mb / upload_time) * 8  # Convert MB/s to Mbps
            self.stdout.write(f"Upload speed: {speed_mbps:.2f} Mbps")

        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Upload failed with status code: {response.status_code}"
                )
            )
            self.stdout.write(f"Response content: {response.content}")

        # Clean up
        item.delete()
        self.stdout.write("Test completed and cleaned up")
