from django.apps import AppConfig
import json

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule

            blog_schedule, _ = IntervalSchedule.objects.get_or_create(
                every=140,
                period=IntervalSchedule.SECONDS,
            )

            user_schedule, _ = IntervalSchedule.objects.get_or_create(
                every=60,
                period=IntervalSchedule.SECONDS,
            )

            PeriodicTask.objects.get_or_create(
                interval=blog_schedule,
                name='Run Blog Embedding Scheduler',
                task='blog.worker.tasks.compute_blog_embedding_task',
                defaults={'args': json.dumps([])},
            )

            PeriodicTask.objects.get_or_create(
                interval=user_schedule,
                name='Run User Embedding Scheduler',
                task='blog.worker.tasks.compute_user_embedding_task',
                defaults={'args': json.dumps([])},
            )

        except Exception as e:
            print(f"[Scheduler Init] ⚠️ Skipped setting up task due to: {e}")
