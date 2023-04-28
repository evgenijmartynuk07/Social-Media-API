from django.contrib.auth import get_user_model
from rest_framework import serializers

from media_post.models import Post
from user.serializers import UserProfileListSerializer


class PostListCreateSerializer(serializers.ModelSerializer):
    author = serializers.EmailField(source="user.user.email", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "hashtag", "text_content", "media_attachment", "author")

    def create(self, validated_data):
        user = self.context["request"].user.userprofile
        validated_data["user"] = user
        return super().create(validated_data)


class PostDetailSerializer(serializers.ModelSerializer):
    user = UserProfileListSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "text_content", "media_attachment", "user")
