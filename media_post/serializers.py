from rest_framework import serializers

from media_post.models import Post, Comment, Like
from user.serializers import UserProfileListSerializer


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.user.id", read_only=True)
    user_email = serializers.EmailField(
        source="user.user.email", read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "text_content",
            "post",
            "user_id",
            "user_email",
            "created_at",
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("text_content", "post", "user")

    def create(self, validated_data):
        user = self.context["request"].user.userprofile
        post = self.context["post"]
        validated_data["user"] = user
        validated_data["post"] = post
        return super().create(validated_data)


class PostListCreateSerializer(serializers.ModelSerializer):
    author = serializers.EmailField(source="user.user.email", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "hashtag",
            "text_content",
            "media_attachment",
            "author",
        )

    def create(self, validated_data):
        user = self.context["request"].user.userprofile
        validated_data["user"] = user
        return super().create(validated_data)


class PostDetailSerializer(serializers.ModelSerializer):
    user = UserProfileListSerializer(read_only=True)
    comments = CommentSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "hashtag",
            "text_content",
            "media_attachment",
            "user",
            "comments",
        )


class PostCreateScheduleSerializer(serializers.ModelSerializer):
    publish_time = serializers.DateTimeField()
    user = UserProfileListSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "hashtag",
            "text_content",
            "media_attachment",
            "user",
            "publish_time",
        )

    def create(self, validated_data):
        user = self.context["request"].user.userprofile
        validated_data["user"] = user
        return super().create(validated_data)


class LikeListSerializer(serializers.ModelSerializer):
    post = PostDetailSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = (
            "user",
            "post",
        )


class LikeCreateSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = (
            "user",
            "post",
        )

    def create(self, validated_data):
        user = self.context["request"].user.userprofile
        post = self.context["post"]
        validated_data["user"] = user
        validated_data["post"] = post
        return super().create(validated_data)
