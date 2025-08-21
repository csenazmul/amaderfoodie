from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """Recipe category model"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Description')
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True,
        verbose_name='Category Image'
    )
    recipe_count = models.PositiveIntegerField(default=0, verbose_name='Recipe Count')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_image_url(self):
        """Return category image URL or default"""
        if self.image:
            return self.image.url
        return f"https://picsum.photos/seed/{self.name}/400/300.jpg"


class Ingredient(models.Model):
    """Recipe ingredient model"""
    
    UNIT_CHOICES = [
        ('', 'Select Unit'),
        ('tsp', 'Teaspoon'),
        ('tbsp', 'Tablespoon'),
        ('cup', 'Cup'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('ml', 'Milliliter'),
        ('l', 'Liter'),
        ('piece', 'Piece'),
        ('clove', 'Clove'),
        ('slice', 'Slice'),
        ('bunch', 'Bunch'),
        ('pinch', 'Pinch'),
        ('to_taste', 'To Taste'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Ingredient Name')
    quantity = models.CharField(max_length=50, verbose_name='Quantity')
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        blank=True,
        verbose_name='Unit'
    )
    
    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['name']
    
    def __str__(self):
        if self.unit:
            return f"{self.quantity} {self.unit} {self.name}"
        return f"{self.quantity} {self.name}"


class Recipe(models.Model):
    """Recipe model"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Recipe Title')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name='Description')
    short_description = models.CharField(max_length=300, verbose_name='Short Description')
    
    # Recipe details
    prep_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Prep Time (minutes)'
    )
    cook_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cook Time (minutes)'
    )
    total_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Total Time (minutes)'
    )
    servings = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Servings'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name='Difficulty'
    )
    
    # Recipe content
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ingredients'
    )
    instructions = models.TextField(verbose_name='Instructions')
    tips = models.TextField(blank=True, verbose_name='Tips & Notes')
    
    # Recipe media
    image = models.ImageField(
        upload_to='recipe_images/',
        verbose_name='Recipe Image'
    )
    video_url = models.URLField(blank=True, verbose_name='Video URL')
    
    # Recipe metadata
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes',
        verbose_name='Category'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Tags (comma separated)'
    )
    
    # Nutrition information (optional)
    calories = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Calories per serving'
    )
    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Protein (g)'
    )
    carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Carbohydrates (g)'
    )
    fat = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Fat (g)'
    )
    fiber = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Fiber (g)'
    )
    sugar = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Sugar (g)'
    )
    sodium = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Sodium (mg)'
    )
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0, verbose_name='Views Count')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='Likes Count')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='Comments Count')
    saves_count = models.PositiveIntegerField(default=0, verbose_name='Saves Count')
    
    # Status and timestamps
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    is_premium = models.BooleanField(default=False, verbose_name='Is Premium')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate total time if not set
        if not self.total_time:
            self.total_time = self.prep_time + self.cook_time
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_image_url(self):
        """Return recipe image URL or default"""
        if self.image:
            return self.image.url
        return f"https://picsum.photos/seed/{self.slug}/800/600.jpg"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_average_rating(self):
        """Calculate average rating"""
        ratings = self.ratings.all()
        if ratings:
            total = sum(rating.rating for rating in ratings)
            return round(total / len(ratings), 1)
        return 0
    
    def increment_views(self):
        """Increment views count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_likes(self):
        """Increment likes count"""
        self.likes_count += 1
        self.save(update_fields=['likes_count'])
    
    def decrement_likes(self):
        """Decrement likes count"""
        if self.likes_count > 0:
            self.likes_count -= 1
            self.save(update_fields=['likes_count'])
    
    def increment_comments(self):
        """Increment comments count"""
        self.comments_count += 1
        self.save(update_fields=['comments_count'])
    
    def decrement_comments(self):
        """Decrement comments count"""
        if self.comments_count > 0:
            self.comments_count -= 1
            self.save(update_fields=['comments_count'])
    
    def increment_saves(self):
        """Increment saves count"""
        self.saves_count += 1
        self.save(update_fields=['saves_count'])


class RecipeStep(models.Model):
    """Recipe preparation step model"""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name='Recipe'
    )
    step_number = models.PositiveIntegerField(verbose_name='Step Number')
    title = models.CharField(max_length=200, verbose_name='Step Title')
    description = models.TextField(verbose_name='Description')
    image = models.ImageField(
        upload_to='recipe_step_images/',
        blank=True,
        null=True,
        verbose_name='Step Image'
    )
    timer = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Timer (seconds)'
    )
    
    class Meta:
        verbose_name = 'Recipe Step'
        verbose_name_plural = 'Recipe Steps'
        ordering = ['step_number']
        unique_together = ['recipe', 'step_number']
    
    def __str__(self):
        return f"{self.recipe.title} - Step {self.step_number}"
    
    def get_image_url(self):
        """Return step image URL or default"""
        if self.image:
            return self.image.url
        return f"https://picsum.photos/seed/{self.recipe.slug}-step-{self.step_number}/400/300.jpg"


class RecipeRating(models.Model):
    """Recipe rating model"""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_ratings',
        verbose_name='User'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating'
    )
    review = models.TextField(blank=True, verbose_name='Review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recipe Rating'
        verbose_name_plural = 'Recipe Ratings'
        unique_together = ['recipe', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.recipe.title} ({self.rating}/5)"


class RecipeComment(models.Model):
    """Recipe comment model"""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_comments',
        verbose_name='User'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Parent Comment'
    )
    content = models.TextField(verbose_name='Comment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recipe Comment'
        verbose_name_plural = 'Recipe Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.recipe.title}"
    
    def get_replies_count(self):
        """Get number of replies"""
        return self.replies.count()


class RecipeLike(models.Model):
    """Recipe like model"""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_likes',
        verbose_name='User'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Recipe Like'
        verbose_name_plural = 'Recipe Likes'
        unique_together = ['recipe', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} likes {self.recipe.title}"


class RecipeSave(models.Model):
    """Recipe save/bookmark model"""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='saves',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_recipes',
        verbose_name='User'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Recipe Save'
        verbose_name_plural = 'Recipe Saves'
        unique_together = ['recipe', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} saved {self.recipe.title}"