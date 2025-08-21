from django.contrib import admin

# Register your models here.
from .models import BlogCategory, Blog, Comment, Like


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0  # don’t show empty extra rows
    fields = ("content", "user", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    fields = ("user", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "author", "created_at")
    search_fields = ("title", "description", "content")
    autocomplete_fields = ("author", "category")
    date_hierarchy = "created_at"
    inlines = [CommentInline, LikeInline]  # 👈 show comments & likes inside blog


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "user", "recipe", "blog", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("content",)
    autocomplete_fields = ("user", "recipe", "blog")
    date_hierarchy = "created_at"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "blog", "created_at")
    list_filter = ("created_at", "user")
    autocomplete_fields = ("user", "recipe", "blog")
    date_hierarchy = "created_at"
