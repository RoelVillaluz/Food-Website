from django.test import Client, TestCase
from django.urls import reverse

from foodhub.views.views import IngredientForm, NewRecipeForm, StepForm
from .models import User, Recipe, Ingredient, Step

# Create your tests here.
class FormTests(TestCase):
    def test_new_recipe_form_valid(self):
        form_data = {
            'name': 'Test Recipe',
            'description': 'This is a test recipe',
            'category': 'Dinner',
            'servings': 4,
            'duration': '30 minutes',
            'difficulty': 'Easy',
            'cost': 'Low'
        }
        form = NewRecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ingredient_form_valid(self):
        form_data = {
            'name': 'Test Ingredient',
            'quantity': 1,
            'unit_of_measurement': 'cup'
        }
        form = IngredientForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_step_form_valid(self):
        form_data = {
            'description': 'This is a test step'
        }
        form = StepForm(data=form_data)
        self.assertTrue(form.is_valid())

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='This is a test recipe',
            category='Dinner',
            servings=4,
            duration='30 minutes',
            difficulty='Easy',
            cost='Low',
            user=self.user
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/index.html')

    def test_login_view(self):
        response = self.client.get(reverse('login_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/login_view.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/register.html')

    def test_create_recipe_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('create_recipe'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/create_recipe.html')

    def test_add_ingredient_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_ingredient', kwargs={'recipe_name': self.recipe.name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/add_ingredient.html')

    def test_add_step_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_step', kwargs={'recipe_name': self.recipe.name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/add_step.html')

    def test_recipe_view(self):
        response = self.client.get(reverse('recipe', kwargs={'recipe_name': self.recipe.name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodhub/recipe.html')

        
class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='This is a test recipe',
            category='Dinner',
            servings=4,
            duration='30 minutes',
            difficulty='Easy',
            cost='Low',
            user=self.user
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.name, 'Test Recipe')
        self.assertEqual(self.recipe.description, 'This is a test recipe')
        self.assertEqual(self.recipe.category, 'Dinner')
        self.assertEqual(self.recipe.servings, 4)
        self.assertEqual(self.recipe.duration, '30 minutes')
        self.assertEqual(self.recipe.difficulty, 'Easy')
        self.assertEqual(self.recipe.cost, 'Low')
        self.assertEqual(self.recipe.user, self.user)