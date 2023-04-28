from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from rest_framework import routers
from user.views import CreateUserView, ManageUserView, FollowingViewSet, FollowerViewSet

from user.views import UserProfileViewSet


router = routers.DefaultRouter()
router.register("userprofile", UserProfileViewSet)
router.register("following", FollowingViewSet)
router.register("followers", FollowerViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
] + router.urls

app_name = "user"
