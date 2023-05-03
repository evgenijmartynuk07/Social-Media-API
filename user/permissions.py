from django.shortcuts import get_object_or_404
from rest_framework import permissions

from media_post.models import Comment


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsCommentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        comment_id = view.kwargs.get("comment_id")
        comment = get_object_or_404(Comment, pk=comment_id)
        return comment.user == request.user.userprofile
