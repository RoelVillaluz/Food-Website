import math
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Avg
from django.utils.translation import gettext_lazy as _

# Register your models here.
admin.site.register(User)
admin.site.register(Step)
admin.site.register(Profile)
admin.site.register(Allergen)

class RelatedObjectFilter(SimpleListFilter):
    """Base class for filters that depend on the presence of related objects."""

    def __init__(self, *args, **kwargs):
        self.related_field_name = kwargs.pop('related_field_name', None)
        self.related_model = kwargs.pop('related_model', None)
        self.related_lookup_field = kwargs.pop('related_lookup_field', 'id')
        self.parameter_name = kwargs.pop('parameter_name', 'related_object')
        self.title = kwargs.pop('title', 'Related Objects')

        if not self.related_field_name or not self.related_model:
            raise ValueError("related_field_name and related_model must be provided")
        
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        # Get related objects based on presence of related field
        related_objects = self.related_model.objects.filter(
            **{f'{self.related_field_name}__isnull': False}
        ).distinct()

        return [(obj.id, str(obj)) for obj in related_objects]
    
    def queryset(self, request, queryset):
        if self.value():
            # Filter queryset based on the presence of related field
            return queryset.filter(
                **{f'{self.related_field_name}__{self.related_lookup_field}': self.value()}
            )
        return queryset

class RecipeInShoppingListFilter(RelatedObjectFilter):
    """Filter for recipes that are present in the shopping list."""

    def __init__(self, *args, **kwargs):
        kwargs['related_field_name'] = 'ingredients'
        kwargs['related_model'] = Recipe
        kwargs['related_lookup_field'] = 'id'
        kwargs['parameter_name'] = 'recipe'
        kwargs['title'] = 'Recipes in Shopping List'
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        # Get unique recipes that are associated with any ingredient in the shopping list
        ingredients = Ingredient.objects.filter(shoppinglist__isnull=False).values_list('recipe', flat=True).distinct()
        recipes = Recipe.objects.filter(id__in=ingredients)
        return [(recipe.id, recipe.name) for recipe in recipes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ingredients__recipe_id=self.value()).distinct()
        return queryset
    
class RecipeInMealPlanFilter(RelatedObjectFilter):
    """Filter for recipes that are present in a  mealplan."""

    def __init__(self, *args, **kwargs):
        kwargs['related_field_name'] = 'recipes'
        kwargs['related_model'] = Recipe
        kwargs['related_lookup_field'] = 'id'
        kwargs['parameter_name'] = 'recipe'
        kwargs['title'] = 'Recipes in Mealplan'
        super().__init__(*args, **kwargs)

    def lookups(self, request, *args, **kwargs):
        mealplans = MealPlan.objects.all()
        recipes_in_mealplans = Recipe.objects.filter(mealplan__in=mealplans).distinct()
        return [(recipe.id, recipe.name) for recipe in recipes_in_mealplans]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(recipes__id=self.value()).distinct()
        return queryset
    
class RatingRangeFilter(admin.SimpleListFilter):
    title = _('Rating')
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return [
            ('1-1.9', _('1 to 1.9 Stars')),
            ('2-2.9', _('2 to 2.9 Stars')),
            ('3-3.9', _('3 to 3.9 Stars')),
            ('4-4.9', _('4 to 4.9 Stars')),
            ('5', _('5 Stars')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1-1.9':
            return queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=1, avg_rating__lt=2)
        elif self.value() == '2-2.9':
            return queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=2, avg_rating__lt=3)
        elif self.value() == '3-3.9':
            return queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=3, avg_rating__lt=4)
        elif self.value() == '4-4.9':
            return queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=4, avg_rating__lt=5)
        elif self.value() == '5':
            return queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=5)
        return queryset

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'display_allergens', 'display_avg_rating')
    search_fields = ('name', 'category')
    list_filter = ('category', 'user', 'allergens', 'difficulty', RatingRangeFilter)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(avg_rating=Avg('ratings__rating'))
        return queryset

    def display_allergens(self, obj):
        return ", ".join([allergen.name for allergen in obj.allergens.all()])
    display_allergens.short_description = 'Allergens'

    def display_avg_rating(self, obj):
        return round(obj.avg_rating, 1) if obj.avg_rating else 'No Ratings Yet'
    display_avg_rating.short_description = 'Ratings'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'quantity', 'unit_of_measurement', 'recipe')
    search_fields = ('name', 'recipe')
    list_filter = ('name', 'recipe')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'rating')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe', 'rating')
    # update code later to show only recipes with ratings in list filter

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date', 'display_recipes')
    search_fields = ('name', 'recipes__name', 'date')
    list_filter = (RecipeInMealPlanFilter, 'user')

    def display_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        return ', '.join([recipe.name for recipe in recipes]) + ('...' if obj.recipes.count() > 3 else ' ')
    display_recipes.short_description = 'Recipes'

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_ingredients', 'display_recipes')
    search_fields = ('user',)
    list_filter = (RecipeInShoppingListFilter, 'user')

    def display_recipes(self, obj):
        ingredients = obj.ingredients.all()
        recipes = set(ingredient.recipe for ingredient in ingredients)
        return ', '.join([recipe.name for recipe in recipes]) + ('...' if len(recipes) > 3 else ' ')
    display_recipes.short_description = 'Recipes'

    def display_ingredients(self, obj):
        ingredients = obj.ingredients.all()[:3]
        return ', '.join([ingredient.name for ingredient in ingredients]) + ('...' if obj.ingredients.count() > 3 else ' ')
    display_ingredients.short_description = 'Ingredients'