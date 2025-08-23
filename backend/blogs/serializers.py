from rest_framework import serializers
from .models import Blog, BlogCategory, Comment, Like


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class BlogSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # show username
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Blog
        fields = [
            "id", "title", "description", "image", "content",
            "slug", "author", "category", "category_id",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        category_id = validated_data.pop("category_id", None)
        request = self.context.get("request")
        blog = Blog.objects.create(author=request.user, **validated_data)

        if category_id:
            try:
                blog.category_id = category_id
                blog.save()
            except:
                pass
        return blog

    def update(self, instance, validated_data):
        category_id = validated_data.pop("category_id", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if category_id:
            try:
                category = BlogCategory.objects.get(id=category_id)
                instance.category = category
            except BlogCategory.DoesNotExist:
                pass
        
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "user", "blog", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        return Comment.objects.create(user=request.user, **validated_data)


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "blog", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        like, created = Like.objects.get_or_create(user=request.user, blog=validated_data["blog"])
        return like
