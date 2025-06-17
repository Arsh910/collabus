from django.db import models
from django.conf import settings


class Notification(models.Model):
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_of = models.CharField(max_length=20)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.to_user.username
