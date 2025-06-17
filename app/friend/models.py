from django.db import models


class Friendship(models.Model):
    from_user = models.ForeignKey(
        "user.User", related_name="friendship_sender", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        "user.User", related_name="friendship_receiver", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
