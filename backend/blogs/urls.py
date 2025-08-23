from django.urls import path
from .views import (
    PublicBlogListView, PublicBlogDetailView,
    BlogCategoryListCreateView, BlogCategoryDetailView,
    CommentListCreateView, CommentDetailView,
    LikeListCreateView, LikeDetailView,BlogCreateView,BlogUpdateView
)

urlpatterns = [
   # Blog
    path("blogs/", PublicBlogListView.as_view(), name="blog-list-public"),
    path("blogs/<slug:slug>/", PublicBlogDetailView.as_view(), name="blog-detail-public"),
    
    path("blogs/create/", BlogCreateView.as_view(), name="blog-create"),
    path("blogs/<slug:slug>/edit/", BlogUpdateView.as_view(), name="blog-edit"),
    
    # Category
    path("categories/", BlogCategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<str:pk>/", BlogCategoryDetailView.as_view(), name="category-detail"),
    
    
    # Comments
    path("blogs/<slug:slug>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("blogs/<slug:slug>/comments/<str:pk>/", CommentDetailView.as_view(), name="comment-detail"),

    # Like
    path("blogs/<slug:slug>/likes/", LikeListCreateView.as_view(), name="like-list-create"),
    path("blogs/<slug:slug>/likes/<str:pk>/", LikeDetailView.as_view(), name="like-detail"),
]
