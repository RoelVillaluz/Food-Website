from django.contrib import admin
from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList

# Register your models here.
admin.site.register(User)
admin.site.register(Step)
admin.site.register(Profile)
admin.site.register(Allergen)
admin.site.register(Review)
admin.site.register(MealPlan)
admin.site.register(ShoppingList)

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

