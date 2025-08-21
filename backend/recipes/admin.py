from django.contrib import admin
from .models import (
    Category, Ingredient, Recipe, RecipeStep, RecipeRating,
    RecipeComment, RecipeLike, RecipeSave
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('recipe_count', 'created_at', 'updated_at')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit')
    list_filter = ('unit',)
    search_fields = ('name',)


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1
    fields = ('step_number', 'title', 'description', 'image', 'timer')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'difficulty', 'status', 'is_featured', 'views_count', 'likes_count', 'created_at')
    list_filter = ('status', 'difficulty', 'category', 'is_featured', 'is_premium', 'created_at')
    search_fields = ('title', 'description', 'author__email', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'likes_count', 'comments_count', 'saves_count', 'created_at', 'updated_at', 'published_at')
    filter_horizontal = ('ingredients',)
    inlines = [RecipeStepInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'author', 'category')
        }),
        ('Recipe Details', {
            'fields': ('prep_time', 'cook_time', 'total_time', 'servings', 'difficulty')
        }),
        ('Content', {
            'fields': ('ingredients', 'instructions', 'tips')
        }),
        ('Media', {
            'fields': ('image', 'video_url')
        }),
        ('Metadata', {
            'fields': ('tags', 'status', 'is_featured', 'is_premium')
        }),
        ('Nutrition Information', {
            'fields': ('calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'saves_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'step_number', 'title', 'timer')
    list_filter = ('recipe__category', 'recipe__difficulty')
    search_fields = ('recipe__title', 'title', 'description')


@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('recipe__title', 'user__email', 'review')


@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('recipe__title', 'user__email', 'content')


@admin.register(RecipeLike)
class RecipeLikeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('recipe__title', 'user__email')


@admin.register(RecipeSave)
class RecipeSaveAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('recipe__title', 'user__email')