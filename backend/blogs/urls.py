from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogCategoryViewSet, BlogViewSet, CommentViewSet, LikeViewSet

# Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'categories', BlogCategoryViewSet, basename='category')
router.register(r'blogs', BlogViewSet, basename='blog')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')

schema_view = get_schema_view(
    openapi.Info(
        title="My Blog API",
        default_version="v1",
        description="API documentation for Blog, Comments, and Likes",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/', include(router.urls)),

    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]


# http://127.0.0.1:8000/swagger/ → Swagger UI
# http://127.0.0.1:8000/redoc/ → ReDoc UI
# http://127.0.0.1:8000/swagger.json/ → Raw OpenAPI JSON

# GET /api/blogs/
# POST /api/blogs/
# GET /api/blogs/{id}/