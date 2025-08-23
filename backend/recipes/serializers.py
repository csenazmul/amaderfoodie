from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Ingredient, Recipe, RecipeStep, RecipeRating,
    RecipeComment, RecipeLike, RecipeSave
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    recipe_count = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url', 'recipe_count', 'created_at']
        read_only_fields = ['slug', 'recipe_count', 'created_at']
    
    def get_image_url(self, obj):
        return obj.get_image_url()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'unit']


class RecipeStepSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeStep
        fields = ['id', 'step_number', 'title', 'description', 'image', 'image_url', 'timer']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        return obj.get_image_url()


class RecipeRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = RecipeRating
        fields = ['id', 'user', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class RecipeCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeComment
        fields = [
            'id', 'user', 'parent', 'content', 'replies', 'replies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return RecipeCommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_replies_count(self, obj):
        return obj.get_replies_count()


class RecipeLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = RecipeLike
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class RecipeSaveSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = RecipeSave
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class RecipeListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'slug', 'short_description', 'image', 'image_url',
            'author', 'category', 'prep_time', 'cook_time', 'total_time',
            'servings', 'difficulty', 'average_rating', 'views_count',
            'likes_count', 'comments_count', 'saves_count', 'is_featured',
            'is_premium', 'created_at', 'published_at'
        ]
    
    def get_image_url(self, obj):
        return obj.get_image_url()
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = RecipeStepSerializer(many=True, read_only=True)
    ratings = RecipeRatingSerializer(many=True, read_only=True)
    comments = RecipeCommentSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'image', 'image_url', 'video_url', 'author', 'category',
            'prep_time', 'cook_time', 'total_time', 'servings', 'difficulty',
            'ingredients', 'steps', 'instructions', 'tips', 'tags', 'tags_list',
            'calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium',
            'views_count', 'likes_count', 'comments_count', 'saves_count',
            'average_rating', 'ratings', 'comments', 'is_featured', 'is_premium',
            'status', 'is_liked', 'is_saved', 'user_rating',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'views_count', 'likes_count', 'comments_count',
            'saves_count', 'average_rating', 'ratings', 'comments',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_image_url(self, obj):
        return obj.get_image_url()
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecipeLike.objects.filter(recipe=obj, user=request.user).exists()
        return False
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecipeSave.objects.filter(recipe=obj, user=request.user).exists()
        return False
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = RecipeRating.objects.get(recipe=obj, user=request.user)
                return rating.rating
            except RecipeRating.DoesNotExist:
                return None
        return None


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    steps = RecipeStepSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'short_description', 'prep_time',
            'cook_time', 'total_time', 'servings', 'difficulty',
            'ingredients', 'steps', 'instructions', 'tips',
            'image', 'video_url', 'category', 'tags',
            'calories', 'protein', 'carbohydrates', 'fat', 'fiber',
            'sugar', 'sodium', 'status', 'is_featured', 'is_premium'
        ]
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        steps_data = validated_data.pop('steps')
        
        # Create recipe
        recipe = Recipe.objects.create(**validated_data)
        
        # Create ingredients
        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_data['name'],
                quantity=ingredient_data['quantity'],
                unit=ingredient_data.get('unit', '')
            )
            recipe.ingredients.add(ingredient)
        
        # Create steps
        for step_data in steps_data:
            RecipeStep.objects.create(recipe=recipe, **step_data)
        
        # Update author's recipe count
        recipe.author.increment_recipes_count()
        
        return recipe
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        steps_data = validated_data.pop('steps', None)
        
        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    quantity=ingredient_data['quantity'],
                    unit=ingredient_data.get('unit', '')
                )
                instance.ingredients.add(ingredient)
        
        # Update steps if provided
        if steps_data is not None:
            instance.steps.all().delete()
            for step_data in steps_data:
                RecipeStep.objects.create(recipe=instance, **step_data)
        
        return instance


class RecipeUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)
    steps = RecipeStepSerializer(many=True, required=False)
    
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'short_description', 'prep_time',
            'cook_time', 'total_time', 'servings', 'difficulty',
            'ingredients', 'steps', 'instructions', 'tips',
            'image', 'video_url', 'category', 'tags',
            'calories', 'protein', 'carbohydrates', 'fat', 'fiber',
            'sugar', 'sodium', 'status', 'is_featured', 'is_premium'
        ]
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        steps_data = validated_data.pop('steps', None)
        
        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    quantity=ingredient_data['quantity'],
                    unit=ingredient_data.get('unit', '')
                )
                instance.ingredients.add(ingredient)
        
        # Update steps if provided
        if steps_data is not None:
            instance.steps.all().delete()
            for step_data in steps_data:
                RecipeStep.objects.create(recipe=instance, **step_data)
        
        return instance