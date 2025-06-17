"""Test for socketio server"""

import asyncio
import socketio
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

SOCKET_IO_URL = "ws://socket.io:8001"
LOGIN_URL = reverse("user:login")


def create_socket_conection(recieved):
    sio = socketio.AsyncClient()

    @sio.on("connection_success", namespace="/notifications")
    async def connection_success(data):
        recieved["msg"] = data

    return sio


class TestSocketIOServer(TestCase):
    def setUp(self):
        self.client = APIClient()
        payload = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "test123",
        }
        self.user = get_user_model().objects.create_user(**payload)

    def test_usersocket_connection(self):
        asyncio.run(self.run_socketio_notification())

    async def run_socketio_notification(self):
        recieved = {}
        sio = create_socket_conection(recieved)

        await sio.connect(
            SOCKET_IO_URL,
            namespaces=["/notifications"],
            auth={
                "token": "111",
                "test": True,
                "username": self.user.username,
                "id": self.user.id,
            },
        )
        await asyncio.sleep(1)

        self.assertIn("msg", recieved)
        self.assertIn("Welcome", recieved["msg"])

        await sio.disconnect()
