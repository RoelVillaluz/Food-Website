from django.contrib import admin
from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Step)
admin.site.register(Recipe)
admin.site.register(Profile)
admin.site.register(Allergen)
admin.site.register(Review)