"""socketio server"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Project.settings")
django.setup()

import socketio
from django.conf import settings
from notifications.notify.notification_namespace import NotificationNamespace

if settings.USE_REDIS_SOCKETIO:
    import redis.asyncio as redis
    mgr = socketio.AsyncRedisManager(settings.REDIS_URL)
else:
    mgr = None

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins="*", client_manager=mgr
)
socketio_app = socketio.ASGIApp(sio)

sio.register_namespace(NotificationNamespace("/notifications"))
