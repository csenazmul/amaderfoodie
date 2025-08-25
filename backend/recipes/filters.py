import django_filters
from django.db.models import Q
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Custom filter for recipes"""
    
    min_prep_time = django_filters.NumberFilter(field_name='prep_time', lookup_expr='gte')
    max_prep_time = django_filters.NumberFilter(field_name='prep_time', lookup_expr='lte')
    
    min_cook_time = django_filters.NumberFilter(field_name='cook_time', lookup_expr='gte')
    max_cook_time = django_filters.NumberFilter(field_name='cook_time', lookup_expr='lte')
    
    min_total_time = django_filters.NumberFilter(field_name='total_time', lookup_expr='gte')
    max_total_time = django_filters.NumberFilter(field_name='total_time', lookup_expr='lte')
    
    min_servings = django_filters.NumberFilter(field_name='servings', lookup_expr='gte')
    max_servings = django_filters.NumberFilter(field_name='servings', lookup_expr='lte')
    
    difficulty = django_filters.ChoiceFilter(choices=Recipe.DIFFICULTY_CHOICES)
    
    category = django_filters.CharFilter(field_name='category__slug')
    
    tags = django_filters.CharFilter(method='filter_tags')
    
    author = django_filters.CharFilter(field_name='author__email')
    
    has_nutrition = django_filters.BooleanFilter(method='filter_has_nutrition')
    
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Recipe
        fields = {
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_premium': ['exact'],
            'difficulty': ['exact'],
            'category': ['exact'],
        }
    
    def filter_tags(self, queryset, name, value):
        """Filter by tags (comma separated)"""
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            q = Q()
            for tag in tags:
                q |= Q(tags__icontains=tag)
            return queryset.filter(q)
        return queryset
    
    def filter_has_nutrition(self, queryset, name, value):
        """Filter recipes that have nutrition information"""
        if value:
            return queryset.filter(
                Q(calories__isnull=False) |
                Q(protein__isnull=False) |
                Q(carbohydrates__isnull=False) |
                Q(fat__isnull=False)
            )
        return queryset
    
    def filter_min_rating(self, queryset, name, value):
        """Filter recipes by minimum average rating"""
        if value:
            return queryset.annotate(
                avg_rating=django_filters.Avg('ratings__rating')
            ).filter(avg_rating__gte=value)
        return queryset