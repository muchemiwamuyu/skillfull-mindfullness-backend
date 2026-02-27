from rest_framework import serializers
from .models import BlogPost, Comment, Like

# relevant serializers
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class BlogPostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "user",
            "title",
            "slug",
            "content",
            "image",
            "relevant_link",
            "is_published",
            "likes_count",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "slug",
            "likes_count",
            "created_at",
            "updated_at",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "post", "created_at"]
        read_only_fields = ["id", "created_at"]