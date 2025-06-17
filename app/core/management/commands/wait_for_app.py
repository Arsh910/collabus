import socket
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        host = "app"
        port = 8000
        timeout = 30

        self.stdout.write(f"Waiting for {host}:{port}...")

        end = time.time() + timeout
        while time.time() < end:
            try:
                socket.create_connection((host, port), timeout=2).close()
                self.stdout.write(self.style.SUCCESS("App is up"))
                return
            except OSError:
                time.sleep(1)
                self.stderr.write(self.style.ERROR("App not available"))
