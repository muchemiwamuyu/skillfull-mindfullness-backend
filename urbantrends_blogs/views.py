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
    
    def get_permissions(self):
        # Specific actions that require a logged-in user
        if self.action in ['create', 'like', 'comment']:
            return [permissions.IsAuthenticated()]
        # Actions that require ownership (Update/Delete)
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        # Everything else (List/Retrieve) is public
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
        
        if user.is_authenticated and user.is_staff:
            return queryset
            
        if user.is_authenticated:
            return queryset.filter(
                models.Q(is_published=True) | models.Q(user=user)
            )

        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # --- CUSTOM ACTIONS ---

    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        """
        Toggles a like: If it exists, delete it. If not, create it.
        URL: POST /api/blogs/posts/{slug}/like/
        """
        post = self.get_object()
        user = request.user
        
        # Check if this user has already liked this specific post
        like_qs = Like.objects.filter(user=user, post=post)

        if like_qs.exists():
            like_qs.delete()
            return Response({"detail": "Unliked", "liked": False}, status=status.HTTP_200_OK)
        
        Like.objects.create(user=user, post=post)
        return Response({"detail": "Liked", "liked": True}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def comment(self, request, slug=None):
        """
        Adds a comment to a specific post.
        URL: POST /api/blogs/posts/{slug}/comment/
        """
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the comment with the current user and the post from the URL
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)