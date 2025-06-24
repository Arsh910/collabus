import sys
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pathlib import Path
from faker import Faker
from blog.models import Blogs

# from django.db.models.signals import post_save
# from blog.signals import handle_new_blog_embedding

fake = Faker()


class Command(BaseCommand):
    help = "Create blog posts from a CSV file using author IDs"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the blogs CSV file")

    def handle(self, *args, **options):

        csv.field_size_limit(sys.maxsize)
        csv_path = Path(options["csv_path"])

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            cleaned_lines = (line.replace("\x00", "") for line in f)
            reader = csv.DictReader(cleaned_lines)

            count = 0
            for row in reader:
                try:
                    author_id = int(row["id"].strip())
                    title = fake.sentence(nb_words=6)
                    content = row["text"].strip()

                    author = get_user_model().objects.get(name=f"Author{author_id}")

                    Blogs.objects.create(title=title, text=content, user=author)
                    count += 1

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully created {title} blog posts.")
                    )

                except get_user_model().DoesNotExist:
                    self.stderr.write(
                        f'⚠️  Author with id {author_id} not found. Skipping blog "{title}".'
                    )
                except Exception as e:
                    self.stderr.write(
                        f'⚠️  Error creating blog "{row.get("title", "[no title]")}": {e}'
                    )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {count} blog posts.")
            )
