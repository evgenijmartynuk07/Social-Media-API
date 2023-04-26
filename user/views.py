from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import UserProfile
from user.serializers import UserSerializer, UserProfileSerializer, UserProfileDetailSerializer, \
    UserProfileCreateSerializer


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
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileSerializer

        if self.action == "retrieve":
            return UserProfileDetailSerializer

        if self.action == "create":
            return UserProfileCreateSerializer

        # if self.action == "upload_image":
        #     return MovieImageSerializer

        return UserProfileSerializer

    def create(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile:
            serializer = self.get_serializer(instance=user_profile, data=request.data)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    # @action(
    #     methods=["POST"],
    #     detail=True,
    #     url_path="upload-image",
    #     permission_classes=[IsAdminUser],
    # )
    # def upload_image(self, request, pk=None):
    #     """Endpoint for uploading image to specific movie"""
    #     movie = self.get_object()
    #     serializer = self.get_serializer(movie, data=request.data)
    #
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)














