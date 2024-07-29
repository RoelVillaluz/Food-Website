from django.contrib import admin
from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList

# Register your models here.
admin.site.register(User)
admin.site.register(Step)
admin.site.register(Profile)
admin.site.register(Allergen)
admin.site.register(Review)

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

    def display_recipes(self, obj):
        ingredients = obj.ingredients.all()
        recipes = set(ingredient.recipe for ingredient in ingredients)
        return ', '.join([recipe.name for recipe in recipes]) + ('...' if len(recipes) > 3 else ' ')
    display_recipes.short_description = 'Recipes'

    def display_ingredients(self, obj):
        ingredients = obj.ingredients.all()[:3]
        return ', '.join([ingredient.name for ingredient in ingredients]) + ('...' if obj.ingredients.count() > 3 else ' ')
    display_ingredients.short_description = 'Ingredients'