from django.contrib.auth import get_user_model
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
from media_post.serializers import PostListCreateSerializer, PostDetailSerializer, CommentSerializer, \
    CommentCreateSerializer, LikeSerializer, PostUpdateSerializer
from user.models import Follow
from user.permissions import IsOwnerOrReadOnly, IsOwner


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
        following_users = Follow.objects.filter(user__user=self.request.user).values_list("following")
        self.queryset = Post.objects.filter(Q(user__user=self.request.user) & Q(user_id__in=following_users))
        return self.queryset

    def get_permissions(self):
        if self.action in ("destroy", "update"):
            return (IsOwner(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action in ("list", "post"):
            return PostListCreateSerializer
        if self.action in ("comments",):
            return CommentSerializer
        if self.action in ("create_comment", "update_comment"):
            return CommentCreateSerializer
        if self.action in ("likes", "like_create"):
            return LikeSerializer
        return PostDetailSerializer

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="comments",
    )
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment-create",
        permission_classes=[IsAuthenticated],
    )
    def create_comment(self, request, pk):
        post = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data,
            context={"request": request, "post": post},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(parameters=[OpenApiParameter("comment_id", str, OpenApiParameter.PATH)])
    @action(
        methods=["PATCH"],
        detail=True,
        url_path="comments/(?P<comment_id>[^/.]+)/update",
        permission_classes=[IsOwnerOrReadOnly],
    )
    def update_comment(self, request, pk, comment_id):
        post = self.get_object()
        comment = post.comments.get(pk=comment_id)

        serializer = CommentCreateSerializer(
            instance=comment,
            data=request.data,
            context={"request": request, "post": post},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(parameters=[OpenApiParameter("comment_id", str, OpenApiParameter.PATH)])
    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsOwnerOrReadOnly],
        url_path="comments/(?P<comment_id>[^/.]+)/delete",
    )
    def destroy_comment(self, request, pk=None, comment_id=None):
        post = self.get_object()
        try:
            comment = post.comments.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404

        if request.user.id != comment.user.user.id:
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsOwner],
        url_path="likes",
    )
    def likes(self, request, pk=None):
        post = self.get_object()
        likes = post.likes.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="like-create",
    )
    def like_create(self, request, pk):
        post = self.get_object()
        user = request.user

        try:
            Like.objects.get(post=post, user__user=user)
        except Like.DoesNotExist:
            serializer = LikeSerializer(data=request.data, context={"request": request, "post": post})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsOwnerOrReadOnly],
        url_path="like-delete",
    )
    def destroy_comment(self, request, pk=None):
        post = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(post=post, user__user=user)
        except Like.DoesNotExist:
            raise Http404

        if request.user.id != like.user.user.id:
            return Response(
                {"detail": "You do not have permission to delete this like."},
                status=status.HTTP_403_FORBIDDEN,
            )

        like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        return super().list(request, *args, **kwargs)

