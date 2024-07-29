from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count

# Register your models here.
admin.site.register(User)
admin.site.register(Step)
admin.site.register(Profile)
admin.site.register(Allergen)
admin.site.register(Review)

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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'display_allergens')
    search_fields = ('name', 'category')
    list_filter = ('category', 'user', 'allergens', 'difficulty')

    def display_allergens(self, obj):
        return ", ".join([allergen.name for allergen in obj.allergens.all()])
    display_allergens.short_description = 'Allergens'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'quantity', 'unit_of_measurement', 'recipe')
    search_fields = ('name', 'recipe')
    list_filter = ('name', 'recipe')

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date', 'display_recipes')
    search_fields = ('name', 'recipes__name', 'date')
    list_filter = ('recipes', 'user')

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