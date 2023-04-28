from django.db import models
from django.utils.translation import gettext as _
import os
import uuid
from django.utils.text import slugify
from user.models import UserProfile


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.user.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post/", filename)


class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    hashtag = models.CharField(max_length=50, blank=True)
    text_content = models.TextField(max_length=1000, blank=True)
    media_attachment = models.ImageField(upload_to=post_image_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
