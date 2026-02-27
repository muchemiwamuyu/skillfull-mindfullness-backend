from django.db import models
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BlogPost, Comment, Like
from .serializers import BlogPostSerializer, CommentSerializer


class IsOwnerOrReadOnly(BasePermission):
    """
    Only the owner of the post can edit or delete it.
    Read permissions are allowed to any request.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class BlogPostViewSet(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            BlogPost.objects
            .select_related("user")
            .prefetch_related("comments", "likes")
            .annotate(likes_count=Count("likes"))
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                models.Q(is_published=True) |
                models.Q(user=self.request.user)
            )

        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, slug=None):
        post = self.get_object()

        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )

        if not created:
            like.delete()
            return Response(
                {"detail": "Unliked"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Liked"},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def comment(self, request, slug=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )