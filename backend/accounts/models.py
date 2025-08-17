from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """Custom user model for AmaderFoodie platform"""
    
    username = None  # Remove username field
    email = models.EmailField(unique=True, verbose_name='Email Address')
    
    # Profile fields
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Bio')
    location = models.CharField(max_length=100, blank=True, verbose_name='Location')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone Number')
    website = models.URLField(blank=True, verbose_name='Website')
    
    # Profile image
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name='Profile Image'
    )
    
    # Cover image
    cover_image = models.ImageField(
        upload_to='cover_images/',
        blank=True,
        null=True,
        verbose_name='Cover Image'
    )
    
    # Social media links
    facebook = models.URLField(blank=True, verbose_name='Facebook Profile')
    twitter = models.URLField(blank=True, verbose_name='Twitter Profile')
    instagram = models.URLField(blank=True, verbose_name='Instagram Profile')
    linkedin = models.URLField(blank=True, verbose_name='LinkedIn Profile')
    
    # Chef specific fields
    is_chef = models.BooleanField(default=False, verbose_name='Is Professional Chef')
    chef_experience = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name='Years of Experience'
    )
    specialties = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Specialties (comma separated)'
    )
    
    # Preferences
    email_notifications = models.BooleanField(default=True, verbose_name='Email Notifications')
    marketing_emails = models.BooleanField(default=False, verbose_name='Marketing Emails')
    
    # Stats
    recipes_count = models.PositiveIntegerField(default=0, verbose_name='Recipes Count')
    blogs_count = models.PositiveIntegerField(default=0, verbose_name='Blogs Count')
    followers_count = models.PositiveIntegerField(default=0, verbose_name='Followers Count')
    following_count = models.PositiveIntegerField(default=0, verbose_name='Following Count')
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    is_premium = models.BooleanField(default=False, verbose_name='Premium User')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def get_specialties_list(self):
        """Return specialties as a list"""
        if self.specialties:
            return [specialty.strip() for specialty in self.specialties.split(',')]
        return []
    
    def get_profile_image_url(self):
        """Return profile image URL or default"""
        if self.profile_image:
            return self.profile_image.url
        return f"https://ui-avatars.com/api/?name={self.full_name}&background=random"
    
    def get_cover_image_url(self):
        """Return cover image URL or default"""
        if self.cover_image:
            return self.cover_image.url
        return f"https://picsum.photos/seed/{self.email}/1200/400.jpg"
    
    def increment_recipes_count(self):
        """Increment recipes count"""
        self.recipes_count += 1
        self.save(update_fields=['recipes_count'])
    
    def decrement_recipes_count(self):
        """Decrement recipes count"""
        if self.recipes_count > 0:
            self.recipes_count -= 1
            self.save(update_fields=['recipes_count'])
    
    def increment_blogs_count(self):
        """Increment blogs count"""
        self.blogs_count += 1
        self.save(update_fields=['blogs_count'])
    
    def decrement_blogs_count(self):
        """Decrement blogs count"""
        if self.blogs_count > 0:
            self.blogs_count -= 1
            self.save(update_fields=['blogs_count'])