from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'user','name', 'description', 'image', 'date', 'servings', 
                  'allergens', 'category', 'cost', 'difficulty', 'duration']
