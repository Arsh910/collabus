import csv
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Create users with IDs from CSV author column (id), ensuring unique emails and usernames"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        csv_file_path = options["csv_file"]
        created_ids = set()

        with open(csv_file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader((line.replace("\x00", "") for line in file))

            for row in reader:
                try:
                    author_id = int(row["id"])
                except (ValueError, KeyError):
                    self.stderr.write("Invalid row, skipping.")
                    continue

                if (
                    author_id in created_ids
                    or get_user_model()
                    .objects.filter(name=f"Author{author_id}")
                    .exists()
                ):
                    continue

                # Use faker.unique for guaranteed unique fields
                try:
                    user = get_user_model().objects.create_user(
                        username=fake.unique.user_name(),
                        email=fake.unique.email(),
                        name=f"Author{author_id}",
                    )
                    user.set_password("defaultpass123")
                    user.save()
                    created_ids.add(author_id)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created user {user.username} with ID {author_id}"
                        )
                    )
                except Exception as e:
                    self.stderr.write(f"Error creating user ID {author_id}: {e}")
