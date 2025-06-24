from django.core.management.base import BaseCommand
from blog.worker.tasks import compute_blog_all_embedding_task


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        result = compute_blog_all_embedding_task.delay()
        self.stdout.write(self.style.SUCCESS(f"Task queued: {result.id}"))
