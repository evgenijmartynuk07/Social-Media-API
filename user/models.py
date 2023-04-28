import os
import uuid

from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile/", filename)


class UserProfile(models.Model):
    SEX_FIELD = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=profile_image_file_path, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(blank=True, null=True, default="URL not defined")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    sex = models.CharField(max_length=12, choices=SEX_FIELD)

    def __str__(self):
        return f"email: {self.user.email}\'s Profile"


class Follow(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    follower = models.ManyToManyField(UserProfile, related_name="following", null=True, blank=True)
    following = models.ManyToManyField(UserProfile, related_name="followers", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

