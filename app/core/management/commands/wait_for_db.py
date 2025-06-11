"""commmand to wait for db to start before starting the app server"""

from django.core.management.base import BaseCommand
import time

from psycopg2 import OperationalError as Psycopg2OperationError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """handle checks to check when db is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2OperationError, OperationalError):
                self.stdout.write("Database unavailable , waiting for 1 sec")
                time.sleep(1)

            self.stdout.write(self.style.SUCCESS("Database available"))
