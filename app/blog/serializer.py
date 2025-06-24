"""Serializer for blog api"""

from rest_framework import serializers
from blog.models import Blogs


class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blogs
        fields = ["id", "user", "title", "text"]
        read_only_fields = ["id", "user"]
