from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from accounts.models import User
import random, string


def generate_random_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


class BlogCategory(models.Model):
    id = models.CharField(primary_key=True, max_length=8, default=generate_random_id, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(BlogCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    id = models.CharField(primary_key=True, max_length=8, default=generate_random_id, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    content = models.TextField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Blog.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title



class Comment(models.Model):
    id = models.CharField(primary_key=True, max_length=8, default=generate_random_id, editable=False, unique=True)
    content = models.TextField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog}"


class Like(models.Model):
    id = models.CharField(primary_key=True, max_length=8, default=generate_random_id, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "blog")  # user can like a blog only once

    def __str__(self):
        return f"{self.user.username} liked {self.blog}"
