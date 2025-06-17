"""urls for friendship api"""

from django.urls import path
from friend.views import FriendshipAPIView

app_name = "friend"

urlpatterns = [path("friendship/", FriendshipAPIView.as_view(), name="friendship")]
