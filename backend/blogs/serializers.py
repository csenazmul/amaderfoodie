from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog, BlogCategory, Comment, Like


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug"]


class BlogSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(), source="category", write_only=True
    )
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id", "title", "description", "image", "content",
            "category", "category_id", "author",
            "created_at", "updated_at"
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "user", "recipe", "blog", "created_at"]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "recipe", "blog", "created_at"]
