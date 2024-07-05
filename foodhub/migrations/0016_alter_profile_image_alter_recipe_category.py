# Generated by Django 5.0.4 on 2024-05-17 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodhub', '0015_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='default.png', null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=models.CharField(blank=True, choices=[('italian', 'Italian'), ('asian', 'Asian'), ('indian', 'Indian'), ('french', 'French'), ('mexican', 'Mexican'), ('japanese', 'Japanese'), ('chinese', 'Chinese'), ('mediterranean', 'Mediterranean'), ('thai', 'Thai'), ('filipino', 'Filipino'), ('american', 'American'), ('greek', 'Greek'), ('breakfast', 'Breakfast'), ('brunch', 'Brunch'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack'), ('appetizer', 'Appetizer'), ('soup', 'Soup'), ('salad', 'Salad'), ('sandwiches', 'Sandwiches'), ('pizza', 'Pizza'), ('pasta', 'Pasta'), ('seafood', 'Seafood'), ('steak', 'Steak'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan'), ('gluten-free', 'Gluten-Free'), ('dessert', 'Dessert'), ('pastry', 'Pastry'), ('beverage', 'Beverage'), ('cocktail', 'Cocktail')], default=None, max_length=32, null=True),
        ),
    ]
