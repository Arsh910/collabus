from rest_framework import views, status
from friend.serilizer import FriendshipSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from friend.models import Friendship
from rest_framework import permissions


class FriendshipAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FriendshipSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        to_user = request.data.get("to_user")
        from_user = request.user
        to_user = get_object_or_404(get_user_model(), id=to_user)

        try:
            friendship = Friendship.objects.get(from_user=from_user, to_user_id=to_user)
            friendship.delete()
            return Response(
                {"detail": "Unfollowed successfully."}, status=status.HTTP_200_OK
            )
        except Friendship.DoesNotExist:
            return Response(
                {"detail": "Friendship does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
