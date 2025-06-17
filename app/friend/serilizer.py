"""Serializer.py"""

from rest_framework import serializers
from friend.models import Friendship


class FriendshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friendship
        fields = ["to_user"]

    def validate(self, attrs):
        request = self.context["request"]
        from_user = request.user.id
        to_user = attrs.get("to_user")

        if from_user == to_user:
            raise serializers.ValidationError("Can follow yourself")

        return attrs

    def create(self, validated_data):
        validated_data["from_user"] = self.context["request"].user
        return Friendship.objects.create(**validated_data)
