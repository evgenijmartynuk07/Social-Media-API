from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileDetailSerializer(serializers.ModelSerializer):
    first_name = UserSerializer(source="user.first_name", many=False, read_only=True)
    last_name = UserSerializer(source="user.last_name", many=False, read_only=True)
    email = UserSerializer(source="user.email", many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "email",)


class UserProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("profile_picture", "bio", "website", "phone_number", "sex")

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
