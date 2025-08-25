from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.core.cache import cache
from django.conf import settings
from .models import (
    Category, Ingredient, Recipe, RecipeStep, RecipeRating,
    RecipeComment, RecipeLike, RecipeSave
)
from .serializers import (
    CategorySerializer, IngredientSerializer, RecipeListSerializer,
    RecipeDetailSerializer, RecipeCreateSerializer, RecipeUpdateSerializer,
    RecipeRatingSerializer, RecipeCommentSerializer, RecipeLikeSerializer,
    RecipeSaveSerializer
)
from .permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter
from accounts.models import UserActivity


class CategoryListView(generics.ListCreateAPIView):
    """List and create recipe categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'recipe_count', 'created_at']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a recipe category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class RecipeListView(generics.ListCreateAPIView):
    """List and create recipes"""
    queryset = Recipe.objects.filter(status='published')
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ['title', 'description', 'short_description', 'tags', 'author__first_name', 'author__last_name']
    ordering_fields = [
        'created_at', 'updated_at', 'published_at', 'title', 'views_count',
        'likes_count', 'comments_count', 'saves_count', 'average_rating'
    ]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user's recipes if requested
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(author_id=user_id)
        
        # Filter by saved recipes if requested and user is authenticated
        if self.request.query_params.get('saved') == 'true' and self.request.user.is_authenticated:
            saved_recipe_ids = RecipeSave.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=saved_recipe_ids)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateSerializer
        return RecipeListSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_created',
            description=f"User {self.request.user.email} created recipe: {serializer.instance.title}"
        )


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a recipe"""
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RecipeUpdateSerializer
        return RecipeDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment views count
        instance.increment_views()
        
        # Log user activity if authenticated
        if request.user.is_authenticated and request.user != instance.author:
            UserActivity.objects.create(
                user=request.user,
                activity_type='recipe_viewed',
                description=f"User {request.user.email} viewed recipe: {instance.title}",
                related_object_id=instance.id,
                related_object_type='recipe'
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        old_status = serializer.instance.status
        new_instance = serializer.save()
        
        # Log user activity
        activity_type = 'recipe_updated'
        if old_status != new_instance.status and new_instance.status == 'published':
            activity_type = 'recipe_published'
        
        UserActivity.objects.create(
            user=self.request.user,
            activity_type=activity_type,
            description=f"User {self.request.user.email} updated recipe: {new_instance.title}",
            related_object_id=new_instance.id,
            related_object_type='recipe'
        )
    
    def perform_destroy(self, instance):
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_deleted',
            description=f"User {self.request.user.email} deleted recipe: {instance.title}",
            related_object_id=instance.id,
            related_object_type='recipe'
        )
        
        # Decrement author's recipe count
        instance.author.decrement_recipes_count()
        
        super().perform_destroy(instance)


class RecipeRatingView(generics.ListCreateAPIView):
    """List and create recipe ratings"""
    serializer_class = RecipeRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return RecipeRating.objects.filter(recipe_id=recipe_id)
    
    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Check if user already rated this recipe
        existing_rating = RecipeRating.objects.filter(recipe=recipe, user=self.request.user).first()
        if existing_rating:
            existing_rating.rating = serializer.validated_data['rating']
            existing_rating.review = serializer.validated_data.get('review', '')
            existing_rating.save()
            return
        
        serializer.save(recipe=recipe, user=self.request.user)
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_rated',
            description=f"User {self.request.user.email} rated recipe: {recipe.title}",
            related_object_id=recipe.id,
            related_object_type='recipe'
        )


class RecipeCommentView(generics.ListCreateAPIView):
    """List and create recipe comments"""
    serializer_class = RecipeCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return RecipeComment.objects.filter(recipe_id=recipe_id, parent=None)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context
    
    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        serializer.save(recipe=recipe, user=self.request.user)
        
        # Increment recipe comments count
        recipe.increment_comments()
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_commented',
            description=f"User {self.request.user.email} commented on recipe: {recipe.title}",
            related_object_id=recipe.id,
            related_object_type='recipe'
        )


class RecipeLikeView(generics.ListCreateAPIView):
    """List and create recipe likes"""
    serializer_class = RecipeLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return RecipeLike.objects.filter(recipe_id=recipe_id)
    
    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Check if user already liked this recipe
        existing_like = RecipeLike.objects.filter(recipe=recipe, user=self.request.user).first()
        if existing_like:
            existing_like.delete()
            recipe.decrement_likes()
            
            # Log user activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='recipe_unliked',
                description=f"User {self.request.user.email} unliked recipe: {recipe.title}",
                related_object_id=recipe.id,
                related_object_type='recipe'
            )
            
            return Response({'message': 'Recipe unliked'}, status=status.HTTP_200_OK)
        
        serializer.save(recipe=recipe, user=self.request.user)
        
        # Increment recipe likes count
        recipe.increment_likes()
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_liked',
            description=f"User {self.request.user.email} liked recipe: {recipe.title}",
            related_object_id=recipe.id,
            related_object_type='recipe'
        )
        
        return Response({'message': 'Recipe liked'}, status=status.HTTP_201_CREATED)


class RecipeSaveView(generics.ListCreateAPIView):
    """List and create recipe saves"""
    serializer_class = RecipeSaveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return RecipeSave.objects.filter(recipe_id=recipe_id)
    
    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Check if user already saved this recipe
        existing_save = RecipeSave.objects.filter(recipe=recipe, user=self.request.user).first()
        if existing_save:
            existing_save.delete()
            recipe.decrement_saves()
            
            # Log user activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='recipe_unsaved',
                description=f"User {self.request.user.email} unsaved recipe: {recipe.title}",
                related_object_id=recipe.id,
                related_object_type='recipe'
            )
            
            return Response({'message': 'Recipe unsaved'}, status=status.HTTP_200_OK)
        
        serializer.save(recipe=recipe, user=self.request.user)
        
        # Increment recipe saves count
        recipe.increment_saves()
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='recipe_saved',
            description=f"User {self.request.user.email} saved recipe: {recipe.title}",
            related_object_id=recipe.id,
            related_object_type='recipe'
        )
        
        return Response({'message': 'Recipe saved'}, status=status.HTTP_201_CREATED)


class UserRecipeListView(generics.ListAPIView):
    """List user's recipes"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ['title', 'description', 'short_description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'views_count', 'likes_count']
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Recipe.objects.filter(author_id=user_id)


class SavedRecipeListView(generics.ListAPIView):
    """List user's saved recipes"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ['title', 'description', 'short_description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'views_count', 'likes_count']
    
    def get_queryset(self):
        saved_recipe_ids = RecipeSave.objects.filter(user=self.request.user).values_list('recipe_id', flat=True)
        return Recipe.objects.filter(id__in=saved_recipe_ids, status='published')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recipe_search_suggestions(request):
    """Get recipe search suggestions"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return Response({'suggestions': []})
    
    # Cache search suggestions
    cache_key = f"recipe_search_suggestions_{query}"
    suggestions = cache.get(cache_key)
    
    if suggestions is None:
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query),
            status='published'
        )[:10]
        
        suggestions = [
            {
                'id': recipe.id,
                'title': recipe.title,
                'slug': recipe.slug,
                'image_url': recipe.get_image_url()
            }
            for recipe in recipes
        ]
        
        cache.set(cache_key, suggestions, timeout=3600)  # Cache for 1 hour
    
    return Response({'suggestions': suggestions})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@method_decorator(cache_page(3600), name='dispatch')
@vary_on_headers('User-Agent')
def featured_recipes(request):
    """Get featured recipes"""
    recipes = Recipe.objects.filter(
        is_featured=True,
        status='published'
    ).order_by('-created_at')[:6]
    
    serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@method_decorator(cache_page(3600), name='dispatch')
@vary_on_headers('User-Agent')
def popular_recipes(request):
    """Get popular recipes based on views and likes"""
    recipes = Recipe.objects.filter(status='published').order_by(
        '-views_count', '-likes_count', '-created_at'
    )[:12]
    
    serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@method_decorator(cache_page(3600), name='dispatch')
@vary_on_headers('User-Agent')
def recent_recipes(request):
    """Get recent recipes"""
    recipes = Recipe.objects.filter(status='published').order_by('-created_at')[:12]
    
    serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
    return Response(serializer.data)