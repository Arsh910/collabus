from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Friendship
from notifications.models import Notification
from notifications.notify import utils
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Friendship)
def send_follow_notification(sender, instance, created, **kwargs):
    if created:
        follower = instance.from_user
        followed = instance.to_user
        Notification.objects.create(
            to_user=followed,
            type_of="notification",
            message=f"{follower.username} made you their friend.",
        )
        data = {
            "type_of": "notification",
            "message": f"{follower.username} made you their friend.",
        }
        async_to_sync(_send_follow_notification)(followed, data)


async def _send_follow_notification(followed, data):
    await utils.send_notification_to_user(followed.id, followed.username, data)
