from blog.worker.celery import app as celery_app
from blog.worker import tasks

__all__ = ["celery_app"]
