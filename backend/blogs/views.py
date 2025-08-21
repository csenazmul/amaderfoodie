from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Blog, BlogCategory, Comment, Like
from .serializers import BlogSerializer, BlogCategorySerializer, CommentSerializer, LikeSerializer


class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by("-created_at")
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # --- Custom Like Toggle Endpoint ---
    @swagger_auto_schema(
        method="post",
        operation_description="Toggle like/unlike for a blog post",
        responses={
            200: openapi.Response("Like toggled successfully", LikeSerializer),
            400: "Invalid request"
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        blog = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, blog=blog)

        if not created:
            # If like already exists → unlike
            like.delete()
            return Response({"message": "Unliked successfully"}, status=status.HTTP_200_OK)

        return Response({"message": "Liked successfully"}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by("-created_at")
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
