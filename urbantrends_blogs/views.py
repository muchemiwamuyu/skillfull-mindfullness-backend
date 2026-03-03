from django.db import models
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BlogPost, Comment, Like
from .serializers import BlogPostSerializer, CommentSerializer


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # 1. Allow any read-only request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 2. Allow if the user is the owner OR is a superuser/staff
        return obj.user == request.user or request.user.is_staff

class BlogPostViewSet(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    lookup_field = "slug"
    
    # Use a more flexible permission approach
    def get_permissions(self):
        if self.action in ['create', 'like', 'comment']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = (
            BlogPost.objects
            .select_related("user")
            .prefetch_related("comments", "likes")
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )

        user = self.request.user
        
        # Staff/Admins see everything
        if user.is_authenticated and user.is_staff:
            return queryset
            
        # Authenticated users see published posts + their own drafts
        if user.is_authenticated:
            return queryset.filter(
                models.Q(is_published=True) | models.Q(user=user)
            )

        # Anonymous users only see published
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        # Ensure the user is saved as the owner
        serializer.save(user=self.request.user)