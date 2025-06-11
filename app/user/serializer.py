"""Serializers for user api views"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(serializers.ModelSerializer):
    """serializer for user"""

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "username",
            "password",
            "name",
            "bio",
            "private_account",
            "prof_image",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create and return user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class GetTokenPairSerializer(TokenObtainPairSerializer):
    """Custom jwt serializer to accept email"""

    username_field = "email"


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(sefl, value):
        try:
            user = get_user_model().objects.get(email=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("email is not registered")

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = "http://{LINK}:3000/user/reset/" + uid + "/" + token

        data = {
            "subject": "Reset Your Password",
            "body": f"This is an email send to reset password . click on the link : {link}",
            "to_email": value,
        }

        if Util.send_email(data):
            return value
        else:
            raise serializers.ValidationError(
                "something worng with email service , please try again"
            )
