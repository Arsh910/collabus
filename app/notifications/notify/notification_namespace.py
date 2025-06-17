"""namespace for handling notifications"""

from socketio import AsyncNamespace
from jwt import decode
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


class NotificationNamespace(AsyncNamespace):

    async def get_user_from_token(self, token):
        UntypedToken(token)
        payload = decode(token, options={"verify_signature": False})
        user_id = payload.get("user_id")
        return await sync_to_async(get_user_model().objects.get)(id=user_id)

    async def on_connect(self, sid, environ, auth):
        token = auth.get("token") if auth else None
        test = auth.get("test")
        if not token:
            raise ConnectionRefusedError("Unauthorized")
        if test:
            username = auth.get("username")
            id = auth.get("id")
            await self.enter_room(sid, f"notification_room_{id}_{username}")
            print("Connectecd:", sid, f"notification_room_{id}_{username}")
            await self.emit("connection_success", f"Welcome {username}!", to=sid)
        else:
            user = await self.get_user_from_token(token)
            await self.enter_room(sid, f"notification_room_{user.id}_{user.username}")
            print("Connectecd:", sid, f"notification_room_{user.id}_{user.username}")
            await self.emit("connection_success", f"Welcome {user.username}!", to=sid)

    async def on_disconnect(self, sid):
        print("Disconnected:", sid)

    async def on_send_notification(self, sid, data):
        print(f"[Notification] {data}")
