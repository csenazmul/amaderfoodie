from django.contrib import admin
from .models import BlogCategory, Blog, Comment, Like

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('category', 'created_at', 'author')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author', 'category')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'blog', 'created_at', 'updated_at')
    list_display_links = ('id',)
    list_filter = ('created_at', 'blog')
    search_fields = ('content', 'user__username', 'blog__title')
    raw_id_fields = ('user', 'blog')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'blog', 'created_at')
    list_display_links = ('id',)
    list_filter = ('created_at', 'blog')
    search_fields = ('user__username', 'blog__title')
    raw_id_fields = ('user', 'blog')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)