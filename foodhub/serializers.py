from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList
from rest_framework import serializers

        
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit_of_measurement', 'quantity']

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'description', 'image', 'video']

class RecipeSerializer(serializers.ModelSerializer):
    recipe_ingredient = IngredientSerializer(many=True)
    recipe_step = StepSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'user','name', 'description', 'image', 'date', 'servings', 
                  'allergens', 'category', 'cost', 'difficulty', 'duration', 'recipe_ingredient', 'recipe_step']
            