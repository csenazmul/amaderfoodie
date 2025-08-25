from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryListView, CategoryDetailView, RecipeListView, RecipeDetailView,
    RecipeRatingView, RecipeCommentView, RecipeLikeView, RecipeSaveView,
    UserRecipeListView, SavedRecipeListView, recipe_search_suggestions,
    featured_recipes, popular_recipes, recent_recipes
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Recipes
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('<slug:slug>/', RecipeDetailView.as_view(), name='recipe-detail'),
    
    # Recipe interactions
    path('<int:recipe_id>/ratings/', RecipeRatingView.as_view(), name='recipe-ratings'),
    path('<int:recipe_id>/comments/', RecipeCommentView.as_view(), name='recipe-comments'),
    path('<int:recipe_id>/likes/', RecipeLikeView.as_view(), name='recipe-likes'),
    path('<int:recipe_id>/saves/', RecipeSaveView.as_view(), name='recipe-saves'),
    
    # User recipes
    path('user/<int:user_id>/', UserRecipeListView.as_view(), name='user-recipes'),
    path('saved/', SavedRecipeListView.as_view(), name='saved-recipes'),
    
    # Search and suggestions
    path('search-suggestions/', recipe_search_suggestions, name='recipe-search-suggestions'),
    
    # Special collections
    path('featured/', featured_recipes, name='featured-recipes'),
    path('popular/', popular_recipes, name='popular-recipes'),
    path('recent/', recent_recipes, name='recent-recipes'),
]