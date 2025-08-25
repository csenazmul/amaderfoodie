from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import Recipe, RecipeComment, RecipeLike, RecipeSave
from accounts.models import UserActivity


@receiver(post_save, sender=Recipe)
def log_recipe_creation(sender, instance, created, **kwargs):
    """Log recipe creation activity"""
    if created:
        UserActivity.objects.create(
            user=instance.author,
            activity_type='recipe_created',
            description=f"User {instance.author.email} created recipe: {instance.title}",
            related_object_id=instance.id,
            related_object_type='recipe'
        )


@receiver(post_save, sender=RecipeComment)
def log_recipe_comment(sender, instance, created, **kwargs):
    """Log recipe comment activity"""
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='recipe_commented',
            description=f"User {instance.user.email} commented on recipe: {instance.recipe.title}",
            related_object_id=instance.recipe.id,
            related_object_type='recipe'
        )


@receiver(post_save, sender=RecipeLike)
def log_recipe_like(sender, instance, created, **kwargs):
    """Log recipe like activity"""
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='recipe_liked',
            description=f"User {instance.user.email} liked recipe: {instance.recipe.title}",
            related_object_id=instance.recipe.id,
            related_object_type='recipe'
        )


@receiver(post_save, sender=RecipeSave)
def log_recipe_save(sender, instance, created, **kwargs):
    """Log recipe save activity"""
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='recipe_saved',
            description=f"User {instance.user.email} saved recipe: {instance.recipe.title}",
            related_object_id=instance.recipe.id,
            related_object_type='recipe'
        )


@receiver(pre_delete, sender=Recipe)
def update_recipe_counts_on_delete(sender, instance, **kwargs):
    """Update counts when recipe is deleted"""
    # Decrement author's recipe count
    instance.author.decrement_recipes_count()
    
    # Log activity
    UserActivity.objects.create(
        user=instance.author,
        activity_type='recipe_deleted',
        description=f"User {instance.author.email} deleted recipe: {instance.title}",
        related_object_id=instance.id,
        related_object_type='recipe'
    )