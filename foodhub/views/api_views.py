from foodhub.models import Allergen, Ingredient, Recipe, Step
from foodhub.serializers import IngredientSerializer, RecipeSerializer, StepSerializer
from rest_framework import generics


class RecipeListCreateApiView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class RecipeRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = 'pk'


class IngredientListCreateApiView(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class StepListCreateApiView(generics.ListCreateAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer