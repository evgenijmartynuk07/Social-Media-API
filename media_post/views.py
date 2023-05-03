from django.db.models import Q
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.types import OpenApiTypes

from media_post.models import Post, Comment, Like
from media_post.serializers import (
    PostListCreateSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    LikeListSerializer,
    LikeCreateSerializer,
    PostCreateScheduleSerializer,
)
from user.models import Follow, UserProfile
from user.permissions import IsCommentOwner
from user.serializers import UserProfileSerializer
from .tasks import create_post


class PostViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Post.objects.select_related("user")

    def get_queryset(self):
        following_users = Follow.objects.filter(
            user__user=self.request.user
        ).values_list("following")
        queryset = self.queryset(
            Q(user__user=self.request.user) & Q(user_id__in=following_users)
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "post"):
            return PostListCreateSerializer

        if self.action in ("comments",):
            return CommentSerializer

        if self.action in ("create_comment", "update_comment"):
            return CommentCreateSerializer

        if self.action == "create_post":
            return PostCreateScheduleSerializer

        if self.action == "likes":
            return LikeListSerializer

        if self.action == "like_create":
            return LikeCreateSerializer

        return PostDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="post-create-schedule",
    )
    def create_post(self, request):
        """Create schedule Post """
        profile = UserProfile.objects.get(user=request.user)
        profile_serializer = UserProfileSerializer(profile)
        request.data["user"] = profile_serializer.data["id"]
        publish_time = request.data.get("publish_time", False)

        if publish_time:
            create_post.delay(request.data, publish_time)
            return Response(status=status.HTTP_202_ACCEPTED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="comments",
    )
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment-create",
    )
    def create_comment(self, request, pk):
        """Create a new comment for a specific post."""
        post = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "post": post},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        parameters=[OpenApiParameter("comment_id", str, OpenApiParameter.PATH)]
    )
    @action(
        methods=["PATCH"],
        detail=True,
        url_path="comments/(?P<comment_id>[^/.]+)/update",
        permission_classes=[IsCommentOwner],
    )
    def update_comment(self, request, pk, comment_id):
        """Editing our own comment for a specific post"""
        post = self.get_object()
        comment = post.comments.get(pk=comment_id)

        serializer = self.get_serializer(
            instance=comment,
            data=request.data,
            context={"request": request, "post": post},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        parameters=[OpenApiParameter("comment_id", str, OpenApiParameter.PATH)]
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="comments/(?P<comment_id>[^/.]+)/delete",
        permission_classes=[IsCommentOwner],
    )
    def destroy_comment(self, request, pk=None, comment_id=None):
        """Delete our own Comment by id"""
        post = self.get_object()
        try:
            comment = post.comments.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["GET"],
        url_path="likes",
    )
    def likes(self, request, pk=None):
        """Viewing the posts we liked, the result is filtered by a specific user."""
        user = request.user
        posts = Like.objects.all(user__user=user).prefetch_related(
            "user__user"
        )
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        url_path="like-create",
    )
    def like_create(self, request, pk):
        """Add new like for Post if like Does Not Exist"""
        post = self.get_object()
        user = request.user

        try:
            Like.objects.get(post=post, user__user=user)
        except Like.DoesNotExist:
            serializer = self.get_serializer(
                data=request.data, context={"request": request, "post": post}
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["delete"],
        url_path="like-delete",
    )
    def destroy_like(self, request, pk=None):
        """Delete our own like"""
        post = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(post=post, user__user=user)
        except Like.DoesNotExist:
            raise Http404
        like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtag",
                type=OpenApiTypes.STR,
                description="Filter by hashtag(ex. ?hashtag=home)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """U can filter Post by hashtag"""
        return super().list(request, *args, **kwargs)
