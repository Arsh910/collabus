from django.core.management.base import BaseCommand
from blog.recommender.recommend import recommend
from datetime import datetime
import json


class Command(BaseCommand):
    help = "Get blog and author recommendations for a user"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int, help="User ID to recommend for")
        parser.add_argument(
            "--last_visit",
            type=str,
            default=None,
            help="Optional last visit date (YYYY-MM-DD)",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        last_visit_str = options["last_visit"]

        if last_visit_str:
            try:
                last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d")
            except ValueError:
                self.stderr.write("Invalid date format. Use YYYY-MM-DD.")
                return
        else:
            last_visit = datetime(1970, 1, 1)

        result = recommend(user_id, last_visit)

        self.stdout.write(self.style.SUCCESS(json.dumps(result, indent=2)))
