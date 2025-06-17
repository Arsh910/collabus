"""Test for creating friendship"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from notifications.models import Notification
from unittest.mock import patch

# import threading
# import time

# import asyncio
import socketio


LOGIN_URL = reverse("user:login")
FRIEND_URL = reverse("friend:friendship")

SOCKET_IO_URL = "ws://socket.io:8001"


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_socket_conection(recieved):
    sio = socketio.AsyncClient()

    @sio.on("connection_success", namespace="/notifications")
    async def connection_success(data):
        print("\n connected")
        recieved["connection_message"] = data  # Changed key to avoid conflict

    @sio.on(
        "send_notification", namespace="/notifications"
    )  # Ensure this is the event name your server emits
    async def send_notification(data):
        print("\n got notification")
        recieved["notification_message"] = data  # Changed key to avoid conflict

    return sio


class TestFriendshipAPI(TestCase):

    def setUp(self):
        payload1 = {
            "email": "test@example.com",
            "password": "testpass123",
            "username": "testuser",
        }

        payload2 = {
            "email": "test2@example.com",
            "password": "testpass123",
            "username": "test2user",
        }

        self.user = create_user(**payload1)
        self.user_other = create_user(**payload2)

        self.client = APIClient()
        res = self.client.post(LOGIN_URL, payload1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {res.data["access"]}')

    @patch("notifications.notify.utils.send_notification_to_user")
    def test_create_friendship(self, patched_send_notification):
        payload = {"to_user": self.user_other.id}
        patched_send_notification.return_value = None
        res = self.client.post(FRIEND_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.user.refresh_from_db()
        self.assertIn(self.user_other, self.user.friends.all())
        self.assertTrue(Notification.objects.filter(to_user=self.user_other))

    # def test_create_friendship_and_notify_other(self):
    #     payload = {'to_user': self.user_other.id}
    #     received = {}

    #     thread = threading.Thread(
    #         target=self._start_socketio_listener,
    #         args=(received,),
    #         daemon=True
    #     )

    #     thread.start()

    #     print("\n waiting for 2 sec for socket to connect")
    #     time.sleep(2)

    #     print("\n sending post request to make friend")
    #     res = self.client.post(FRIEND_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    #     self.user.refresh_from_db()
    #     self.assertIn(self.user_other, self.user.friends.all())

    #     print("\n waiting for 30 sec for notification")

    #     for _ in range(20):
    #         if "message" in received:
    #             break
    #         time.sleep(1)

    #     self.assertIn("message", received)
    #     self.assertIn("type_of", received["message"])
    #     self.assertIn("message", received["message"])

    # def _start_socketio_listener(self, received):
    #     asyncio.run(self.run_socketio_notification(received))

    # async def run_socketio_notification(self , recieved):
    #     sio = create_socket_conection(recieved)
    #     print("\n connecting notify socket")
    #     await sio.connect(
    #         SOCKET_IO_URL, namespaces=["/notifications"], auth={"token":"111", "test" :True , "username":self.user_other.username ,"id":self.user_other.id}
    #     )
    #     print("\n keeping socket up for 20 sec")
    #     await asyncio.sleep(30)
    #     print("diconnecting")
    #     await sio.disconnect()
