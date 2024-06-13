import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db.models import Avg

# Create your models here.
class User(AbstractUser):
    pass


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'grams'),
        ('kg', 'kilograms'),
        ('mg', 'milligrams'),
        ('lb', 'pounds'),
        ('oz', 'ounces'),
        ('ml', 'milliliters'),
        ('l', 'liters'),
        ('tsp', 'teaspoons'),
        ('tbsp', 'tablespoons'),
        ('cup', 'cups'),
        ('pt', 'pints'),
        ('qt', 'quarts'),
        ('slices', 'slices'),
        ('sticks', 'sticks'),
        ('scoops', 'scoops'),
        ('none', 'none')
    ]

    name = models.CharField(max_length=100)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name="recipe_ingredient", default=None)
    quantity = models.IntegerField()
    unit_of_measurement = models.CharField(max_length=32, choices=UNIT_CHOICES, default=None)

    def __str__(self):
        return f"{self.quantity} {self.unit_of_measurement} of {self.name}"

class Step(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name="recipe_step", default=None)
    description = models.TextField()  
    image = models.ImageField(upload_to="media", blank=True, null=True)
    video = models.FileField(upload_to="videos", blank=True, null=True)

    def __str__(self):
        return self.description

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipe_user")
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="media", blank=True, null=True, default="default.jpg")
    date = models.DateTimeField(default=datetime.datetime.now)
    servings = models.PositiveIntegerField(default=1)
    allergens = models.ManyToManyField('Allergen', blank=True)
    likes = models.ManyToManyField(User, default=None, blank=True, related_name="recipe_likes")

    CATEGORY_CHOICES = (
    ('american', 'American'),
    ('appetizer', 'Appetizer'),
    ('asian', 'Asian'),
    ('beverage', 'Beverage'),
    ('brunch', 'Brunch'),
    ('breakfast', 'Breakfast'),
    ('chinese', 'Chinese'),
    ('cocktail', 'Cocktail'),
    ('dessert', 'Dessert'),
    ('dinner', 'Dinner'),
    ('filipino', 'Filipino'),
    ('french', 'French'),
    ('gluten-free', 'Gluten-Free'),
    ('greek', 'Greek'),
    ('indian', 'Indian'),
    ('italian', 'Italian'),
    ('japanese', 'Japanese'),
    ('lunch', 'Lunch'),
    ('mediterranean', 'Mediterranean'),
    ('mexican', 'Mexican'),
    ('pastry', 'Pastry'),
    ('pasta', 'Pasta'),
    ('pizza', 'Pizza'),
    ('salad', 'Salad'),
    ('sandwiches', 'Sandwiches'),
    ('seafood', 'Seafood'),
    ('snack', 'Snack'),
    ('soup', 'Soup'),
    ('steak', 'Steak'),
    ('thai', 'Thai'),
    ('vegan', 'Vegan'),
    ('vegetarian', 'Vegetarian'),
)


    DURATION_CHOICES = (
        ('15-20 mins', '15-20 mins'),
        ('20-45 mins', '20-45 mins'),
        ('45 mins to 1 hr', '45 mins to 1 hr'),
        ('1 hr+', '1 hr+'),
    )

    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('chef', 'Chef')
    )

    COST_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, blank=True, null=True, default=None)
    duration = models.CharField(max_length=32, choices=DURATION_CHOICES, blank=True, null=True, default=None)
    difficulty = models.CharField(max_length=32, choices=DIFFICULTY_CHOICES, blank=True, null=True, default=None)
    cost = models.CharField(max_length=32, choices=COST_CHOICES, blank=True, null=True, default=None)


    def __str__(self):
        return self.name
    
    def formatted_date(self):
        return self.date.strftime("%B %d, %Y")
    
    def get_breadcrumbs(self):
        return [
            {'label': 'Home', 'url': reverse('index')},
            {'label': 'Recipes', 'url': reverse('recipes')},
            {'label': self.get_category_display(), 'url': reverse('category', args=[self.category])},
            {'label': self.name, 'url': reverse('recipe', args=[self.name])}
        ]

    def first_letter(self):
        return self.category and self.category[0]
    

class Allergen(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
       
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="media", blank=True, null=True)
    allergens = models.ManyToManyField('Allergen', blank=True)
    culinary_level = models.CharField(max_length=32, choices=Recipe.DIFFICULTY_CHOICES, blank=True, null=True, default=None)
    featured_recipe = models.ForeignKey('Recipe', on_delete=models.SET_NULL, related_name='featured_in_profiles', blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='following_profiles', blank=True)

    def __str__(self):
        return str(self.user)

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.user.username}'s review for {self.recipe.name}: {self.rating}"
    
    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0

class MealPlan(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    recipes = models.ManyToManyField(Recipe)
    date = models.DateField()

    def __str__(self):
        return self.name