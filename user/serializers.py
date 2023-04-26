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


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "first_name", "last_name",)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=False)
    first_name = serializers.CharField(source="user.first_name", read_only=False)
    last_name = serializers.CharField(source="user.last_name", read_only=False)

    class Meta:
        model = UserProfile
        fields = ("profile_picture", "bio", "website", "sex", "first_name", "last_name", "email", "phone_number")

    def update(self, instance, validated_data):
        profile = instance
        user = profile.user

        # Update user object if there's any data related to it
        user_data = validated_data.pop("user", {})
        if user_data:
            user_serializer = UserUpdateSerializer(user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update profile object with the remaining validated data
        for key, value in validated_data.items():
            setattr(profile, key, value)
        profile.save()

        return profile


class UserProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("profile_picture", "bio", "website", "phone_number", "sex")

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
