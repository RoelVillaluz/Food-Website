from django.urls import path, re_path
from .views import views
from .views.api_views import IngredientListCreateApiView, RecipeListCreateApiView, RecipeRetrieveUpdateDestroyApiView, StepListCreateApiView

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_recipe", views.create_recipe, name="create_recipe"),
    path("add_ingredient/<str:recipe_name>", views.add_ingredient, name="add_ingredient"),
    path("add_step/<str:recipe_name>", views.add_step, name="add_step"),
    path("add_allergens/<str:recipe_name>", views.add_allergens, name="add_allergens"),
    path("recipes", views.recipes, name="recipes"),
    path("recipe/<str:recipe_name>", views.recipe, name="recipe"),
    path('api/rating-distribution/<int:recipe_id>/', views.rating_distribution, name='rating_distribution'),
    path("edit_recipe/<str:recipe_name>", views.edit_recipe, name="edit_recipe"),
    path("recipe/<str:recipe_name>/create_review", views.create_review, name="create_review"),
    path("like_recipe/<int:id>", views.like_recipe, name="like_recipe"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>/", views.category, name="category"),
    path("ingredients", views.ingredients, name="ingredients"),
    re_path(r'^ingredient/(?P<ingredient>.+)/$', views.ingredient, name='ingredient'),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile_allergen/<str:username>", views.profile_allergen, name="profile_allergen"),
    path("profile/<str:username>/edit", views.edit_profile, name="edit_profile"),
    path("edit_bio", views.edit_bio, name="edit_bio"),
    path("create_mealplan", views.create_mealplan, name="create_mealplan"),
    path('edit_mealplan/<str:date>/', views.edit_mealplan, name="edit_mealplan"),
    path('api/mealplan/<str:date>/', views.get_mealplan_by_date, name='get_mealplan_by_date'),
    path('api/upcoming_mealplans/<str:date>/', views.upcoming_mealplans, name='upcoming_mealplans'),
    path('recipe_recommender', views.recipe_recommender, name="recipe_recommender"),
    path('add_ingredients_to_list/<str:recipe_name>/', views.add_ingredients_to_list, name="add_ingredients_to_list"),
    path('my_shopping_list', views.my_shopping_list, name="my_shopping_list"),
    path('practice', views.practice, name="practice"),

    path('api/recipes/', RecipeListCreateApiView.as_view(), name='recipes-api'),
    path('api/recipes/<int:pk>', RecipeRetrieveUpdateDestroyApiView.as_view(), name='recipes-api-update'),
    path('api/ingredients/', IngredientListCreateApiView.as_view(), name='ingredients-api'),
    path('api/steps/', StepListCreateApiView.as_view(), name='steps-api'),
    path('check_username/', views.check_username, name="check_username")
]