"""function to send notification through backend"""


def get_sio():
    from realtime.socketio_server import sio

    return sio


async def send_notification_to_user(user_id, username, data):
    sio = get_sio()
    print(f"\n sending notification to notification_room_{user_id}_{username}")
    await sio.emit(
        "send_notification",
        data,
        room=f"notification_room_{user_id}_{username}",
        namespace="/notifications",
    )
