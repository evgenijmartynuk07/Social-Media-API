from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from django.urls import reverse
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.types import OpenApiTypes
from user.exceptions import ObjectAlreadyExists, AlreadySubscribeExists
from user.models import UserProfile, Follow
from user.permissions import IsOwnerOrReadOnly
from user.serializers import UserSerializer, UserProfileSerializer, UserProfileDetailSerializer, \
    UserProfileCreateSerializer, UserProfileListSerializer, FollowingSerializer, FollowerSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,

):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = UserProfile.objects.all()

    @action(
        methods=["POST"],
        detail=False,
        url_path="create-profile",
        permission_classes=[IsAuthenticated],
    )
    def create_profile(self, request):
        if UserProfile.objects.filter(user=request.user).exists():
            raise ObjectAlreadyExists()

        create = mixins.CreateModelMixin()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create.perform_create(serializer)
        headers = create.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action in ("list",):
            return UserProfileListSerializer

        if self.action in ("retrieve", "update"):
            return UserProfileDetailSerializer

        if self.action == "create_profile":
            return UserProfileCreateSerializer

        return UserProfileSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type={"type": "list", "items": {"type": "str"}},
                description="Filter by first_name id (ex. ?genres=2,5)",
            ),

        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=OpenApiTypes.STR,
                description="Filter by first_name id (ex. ?first_name=John&first_name=Jane)",
            ),
            OpenApiParameter(
                "last_name",
                type=OpenApiTypes.STR,
                description="Filter by last_name id (ex. ?last_name=John&last_name=Jane)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FollowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Follow.objects.prefetch_related("following")
    serializer_class = FollowingSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(user__user_id=self.request.user.id).exclude(following=None)
        return queryset

    def create(self, request, *args, **kwargs):
        following_user = request.data.get("following")
        if Follow.objects.filter(following=following_user).exists():
            raise AlreadySubscribeExists()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FollowerViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Follow.objects.prefetch_related("follower")
    serializer_class = FollowerSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(user__user_id=self.request.user.id).exclude(follower=None)
        return queryset







