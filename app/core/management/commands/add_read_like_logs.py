import random
from django.core.management.base import BaseCommand
from blog.models import Blogs
from user.models import User
from blog.recommender.logs.mongo import log_read_event, log_like_event


class Command(BaseCommand):
    help = "Generate random read and like logs for all users (excluding their own blogs)"

    def handle(self, *args, **options):
        all_users = list(User.objects.all())
        all_blogs = list(Blogs.objects.all())

        if not all_users or not all_blogs:
            self.stdout.write(self.style.ERROR("❌ No users or blogs found."))
            return

        for user in all_users:
            # Exclude blogs written by the user
            eligible_blogs = [b for b in all_blogs if b.user_id != user.id]

            if len(eligible_blogs) < 10:
                self.stdout.write(self.style.WARNING(f"⚠️ Not enough blogs for user {user.id}, skipping..."))
                continue

            # Randomly pick 10 for read and 5 for like (without overlap)
            read_blogs = random.sample(eligible_blogs, 10)
            like_blogs = random.sample(eligible_blogs, 5)

            for blog in read_blogs:
                log_read_event(user.id, blog.id)
                self.stdout.write(self.style.SUCCESS(f"📖 Logged READ: user {user.id} -> blog {blog.id}"))

            for blog in like_blogs:
                log_like_event(user.id, blog.id)
                self.stdout.write(self.style.SUCCESS(f"❤️ Logged LIKE: user {user.id} -> blog {blog.id}"))

        self.stdout.write(self.style.SUCCESS("✅ Finished logging random reads and likes."))
