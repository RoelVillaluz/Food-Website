from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_recipe", views.create_recipe, name="create_recipe"),
    path("add_ingredient/<str:recipe_name>", views.add_ingredient, name="add_ingredient"),
    path("add_step/<str:recipe_name>", views.add_step, name="add_step"),
    path("recipes", views.recipes, name="recipes"),
    path("recipe/<str:recipe_name>", views.recipe, name="recipe"),
    path("recipe/<str:recipe_name>/create_review", views.create_review, name="create_review"),
    path("like_recipe/<int:id>", views.like_recipe, name="like_recipe"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>/", views.category, name="category"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile_allergen/<str:username>", views.profile_allergen, name="profile_allergen"),
    # path("profile/<str:username>/edit", views.edit_profile, name="edit_profile"),
    path("edit_bio", views.edit_bio, name="edit_bio"),
]