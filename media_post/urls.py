from django.urls import path, include
from rest_framework import routers

from media_post.views import PostViewSet

router = routers.DefaultRouter()
router.register("post", PostViewSet)

urlpatterns = router.urls

app_name = "media_post"
