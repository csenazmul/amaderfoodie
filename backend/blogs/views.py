from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import Blog, BlogCategory, Comment, Like
from .serializers import BlogSerializer, BlogCategorySerializer, CommentSerializer, LikeSerializer
from rest_framework.exceptions import PermissionDenied, NotFound


# -------- BLOG CATEGORY --------
class BlogCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = BlogCategory.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__iexact=name)
        return queryset


class BlogCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# -------- BLOG LIST (Public) --------
class PublicBlogListView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by("-created_at")
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny] 


# -------- BLOG DETAIL (Public) --------
class PublicBlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


# -------- BLOG CREATE (Authenticated) --------
class BlogCreateView(generics.CreateAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


# -------- BLOG UPDATE (Authenticated & Author Only) --------
class BlogUpdateView(generics.UpdateAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return Blog.objects.all()

    def perform_update(self, serializer):
        blog = self.get_object()
        if blog.author != self.request.user:
            raise PermissionDenied("You do not have permission to edit this blog")
        serializer.save()


# -------- COMMENT --------
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise NotFound("Blog not found")
        return Comment.objects.filter(blog=blog).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    def perform_create(self, serializer):
        slug = self.kwargs.get("slug")
        try:
            blog = Blog.objects.get(slug=slug)
            serializer.save(user=self.request.user, blog=blog)
        except Blog.DoesNotExist:
            raise NotFound("Blog not found")

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise NotFound("Blog not found")
        return Comment.objects.filter(blog=blog)


# -------- LIKE --------
class LikeListCreateView(generics.ListCreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise NotFound("Blog not found")
        return Like.objects.filter(blog=blog).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        slug = self.kwargs.get("slug")
        blog = Blog.objects.get(slug=slug)
        serializer.save(user=self.request.user, blog=blog)


class LikeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise NotFound("Blog not found")
        return Like.objects.filter(blog=blog)
