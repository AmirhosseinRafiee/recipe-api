"""
Custom filters to enable advanced data filtering.
"""
from django_filters import FilterSet, filters
from core.models import Recipe, Ingredient, Tag


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class RecipeFilter(FilterSet):
    """Filter recipes."""
    tags_in = NumberInFilter(field_name='tags__id', lookup_expr='in')
    ingredients_in = NumberInFilter(
        field_name='ingredients__id',
        lookup_expr='in'
    )

    class Meta:
        model = Recipe
        fields = []

    def filter_queryset(self, queryset):
        """Distinct queryset."""
        queryset = super().filter_queryset(queryset)
        return queryset.distinct()


class IngredientFilter(FilterSet):
    """Filter ingredients that are assigned to at least one recipe."""
    assigned_only = filters.BooleanFilter(
        field_name='recipe',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = Ingredient
        fields = []


class TagFilter(FilterSet):
    """Filter tags that are assigned to at least one recipe."""
    assigned_only = filters.BooleanFilter(
        field_name='recipe',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = Tag
        fields = []
