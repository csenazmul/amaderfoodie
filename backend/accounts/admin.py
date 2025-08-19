from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Follower, UserActivity

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'is_chef', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('is_chef', 'is_verified', 'is_active', 'is_premium', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'bio', 'location')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'bio', 'location', 'phone')}),
        ('Profile Images', {'fields': ('profile_image', 'cover_image')}),
        ('Professional Info', {'fields': ('is_chef', 'chef_experience', 'specialties')}),
        ('Social Media', {'fields': ('website', 'facebook', 'twitter', 'instagram', 'linkedin')}),
        ('Preferences', {'fields': ('email_notifications', 'marketing_emails')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'is_premium'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'city', 'country', 'language', 'created_at')
    list_filter = ('gender', 'language', 'country', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__email', 'following__email', 'follower__first_name', 'following__first_name')
    readonly_fields = ('created_at',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'description')
    readonly_fields = ('created_at',)