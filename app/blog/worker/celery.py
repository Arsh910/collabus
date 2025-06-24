import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Project.settings")
import django

django.setup()

app = Celery("blog")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
