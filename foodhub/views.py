import random
from urllib.parse import unquote
from django import forms
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q, Avg
from django.contrib import messages
from collections import defaultdict


import json

from django.urls import reverse

from .models import User, Ingredient, Step, Recipe, Profile, Allergen, Review, MealPlan, ShoppingList

class NewRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "description", "image", "category", "servings", "duration", "difficulty", "cost"]
        widgets = {
            'name': forms.TextInput(attrs={"class": "form-control"}),
            'description': forms.Textarea(attrs={"class": "form-control"}),
            'image': forms.FileInput(),
        }
        labels = {
            'name': 'Recipe Name',
            'description': 'Recipe Description',
            'image': 'Upload Image',
        }

    def __init__(self, *args, **kwargs):
        super(NewRecipeForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget = forms.Select(choices=Recipe.CATEGORY_CHOICES, attrs={'class': 'form-control'})
        self.fields['duration'].widget = forms.Select(choices=Recipe.DURATION_CHOICES, attrs={'class': 'form-control'})
        self.fields['difficulty'].widget = forms.Select(choices=Recipe.DIFFICULTY_CHOICES, attrs={'class': 'form-control'})
        self.fields['cost'].widget = forms.Select(choices=Recipe.COST_CHOICES, attrs={'class': 'form-control'})

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit_of_measurement']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['description', 'rating']

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['description', 'image', 'video']

class DateInput(forms.DateInput):
    input_type = 'date'

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['name', 'description', 'recipes', 'date']
        widgets = {
            'date': forms.DateInput(),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'image', 'allergens', 'culinary_level', 'location', 'education']
    
# Create your views here.
def index(request):
    # Select the top 3 recipes with the highest average rating
    popular_recipes = Recipe.objects.annotate(
        avg_rating=Avg('ratings__rating'), 
        review_count=Count('ratings', distinct=True), 
        like_count=Count('likes')).order_by('-avg_rating', '-review_count', '-like_count')[:3]

    # Get the top 5 categories with the most recipes
    category_counts = Recipe.objects.values('category').annotate(total=Count('category')).order_by('-total')[:5]
    category_choices_dict = dict(Recipe.CATEGORY_CHOICES)

    top_categories = []
    for category in category_counts:
        category_name = category_choices_dict[category['category']]
        recipe = Recipe.objects.filter(category=category['category']).last()
        top_categories.append((category_name, recipe))

    return render(request, "foodhub/index.html", {
        "recipes": Recipe.objects.all(),
        "categories": Recipe.CATEGORY_CHOICES,
        "featured_categories": Recipe.CATEGORY_CHOICES[:6],
        "popular": popular_recipes,
        "top_categories": top_categories,
    })

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "foodhub/login_view.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "foodhub/login_view.html")
    
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "foodhub/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        profile = Profile()
        profile.user = user
        profile.save()

        shopping_list = ShoppingList()
        shopping_list.user = user
        shopping_list.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "foodhub/register.html")

    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login_view')
def create_recipe(request):
    if request.method == "POST":
        form = NewRecipeForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            difficulty = form.cleaned_data["difficulty"]
            servings = form.cleaned_data["servings"]
            duration = form.cleaned_data["duration"]
            cost = form.cleaned_data["cost"]
            user = request.user

            # Create the recipe
            recipe = Recipe.objects.create(name=name, description=description, image=image, category=category, difficulty=difficulty, servings=servings, duration=duration, cost=cost, user=user)
            
            # Redirect to the 'add_ingredient' page with the newly created recipe's name as a parameter
            return HttpResponseRedirect(reverse("add_ingredient", kwargs={'recipe_name': recipe.name}))
        else:
            return render(request, "foodhub/create_recipe.html", {
                "form": form,
                "categories": Recipe.CATEGORY_CHOICES,
                "featured_categories": Recipe.CATEGORY_CHOICES[:6]
            })
    else:
        return render(request, "foodhub/create_recipe.html", {
            "form": NewRecipeForm(),
            "categories": Recipe.CATEGORY_CHOICES,
            "featured_categories": Recipe.CATEGORY_CHOICES[:6]
        })
    
@login_required(login_url='/login')
def add_ingredient(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    
    # Handle POST request for adding an ingredient
    if request.method == 'POST' and 'add_ingredient' in request.POST:
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            ingredient.save()
            return redirect("add_ingredient", recipe_name=recipe_name)

    # Handle POST request for deleting an ingredient
    elif request.method == 'POST' and 'delete_ingredient' in request.POST:
        ingredient_id = request.POST.get('delete_ingredient')
        ingredient = Ingredient.objects.get(id=ingredient_id, recipe=recipe)
        ingredient.delete()
        return redirect("add_ingredient", recipe_name=recipe_name)
    
    else:
        form = IngredientForm()
    
    ingredients = Ingredient.objects.filter(recipe=recipe)
    
    return render(request, "foodhub/add_ingredient.html", { 
        "form": form, 
        "recipe": recipe,
        "ingredients": ingredients,
    })

@login_required(login_url='/login')
def add_step(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    if request.method == 'POST':
        form = StepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            video = form.cleaned_data["video"]
            step.recipe = recipe
            Step.objects.create(description=description, image=image, video=video, recipe=recipe)
            return redirect("add_step", recipe_name=recipe_name)
    else:
        form = StepForm()
    return render(request, "foodhub/add_step.html", {
        "form": form,
        "recipe": recipe,
        "steps": Step.objects.filter(recipe=recipe)              
    })

@csrf_exempt
@login_required(login_url='/login')
def add_allergens(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    if request.method == 'POST':
        recipe_allergens = request.POST.getlist("recipe_allergens")
        allergens = Allergen.objects.filter(name__in=recipe_allergens)
        recipe.allergens.set(allergens)
        recipe.save()
        return redirect("recipe", recipe_name=recipe_name)
    else:
        recipe_allergens = recipe.allergens.values_list('name', flat=True)
        return render(request, "foodhub/add_allergens.html", {
            "recipe": recipe,
            "allergens": Allergen.objects.all(),
            "recipe_allergens": recipe_allergens
        })

    
def recipes(request):
    recipes = Recipe.objects.all()
    categories = Recipe.CATEGORY_CHOICES
    featured_categories = Recipe.CATEGORY_CHOICES[:6]
    durations = Recipe.DURATION_CHOICES
    difficulties = Recipe.DIFFICULTY_CHOICES
    costs = Recipe.COST_CHOICES

    # Retrieve search query
    query = request.GET.get('q', '')
    if query:
        recipes = recipes.filter(name__icontains=query)

    # Retrieve selected filter options from the request
    selected_category = request.GET.get('category')
    selected_duration = request.GET.get('duration')
    selected_difficulty = request.GET.get('difficulty')
    selected_cost = request.GET.get('cost')
    selected_rating = request.GET.get('rating')  # Retrieve rating filter

    # Apply filters based on selected options
    if selected_category:
        recipes = recipes.filter(category=selected_category)
    if selected_duration:
        recipes = recipes.filter(duration=selected_duration)
    if selected_difficulty:
        recipes = recipes.filter(difficulty=selected_difficulty)
    if selected_cost:
        recipes = recipes.filter(cost=selected_cost)

    toggle_allergens = request.GET.get('toggle-allergens-btn') == 'on'
    
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
        user_allergens = user_profile.allergens.all()

        if toggle_allergens:
            # Exclude recipes containing user's allergens
            recipes = recipes.exclude(allergens__in=user_allergens)

    toggle_likes = request.GET.get('toggle-likes-btn') == 'on'

    if request.user.is_authenticated:
        if toggle_likes:
            liked_recipes = Recipe.objects.filter(likes=request.user)
            recipes = liked_recipes

    # Calculate average ratings for each recipe
    recipes = recipes.annotate(avg_rating=Avg('ratings__rating'))

    # Filter by selected rating
    if selected_rating:
        # Convert selected_rating to an integer (if necessary)
        selected_rating = int(selected_rating)
        # Define rating range
        rating_start = selected_rating
        rating_end = selected_rating + 0.9
        # Filter recipes by average rating within the range
        recipes = recipes.filter(avg_rating__gte=rating_start, avg_rating__lt=rating_end)

    # Sort filters
    sort_type = request.GET.get('sort', 'name')
    if sort_type in ['name', '-name', 'date', '-date']:
        recipes = recipes.order_by(sort_type)
    else:
        recipes = recipes.order_by("name")

    return render(request, "foodhub/recipes.html", {
        "recipes": recipes,
        "categories": categories,
        "featured_categories": featured_categories,
        "selected_category": selected_category,
        "selected_duration": selected_duration,
        "selected_difficulty": selected_difficulty,
        "sort_type": sort_type,
        "selected_cost": selected_cost,
        "selected_rating": selected_rating,  # Pass selected rating to template
        "durations": durations,
        "difficulties": difficulties,
        "costs": costs,
        "toggle_allergens": toggle_allergens,
        "toggle_likes": toggle_likes,
        "query": query,
    })

    
def recipe(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    average_rating = Review.average_rating(recipe)

    if request.method == 'POST':
        if 'delete' in request.POST:
            recipe.delete()
            messages.success(request, f"Recipe '{recipe_name}' has been deleted successfully.")
            return redirect('recipes')  
        
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.recipe = recipe
            review.user = request.user
            review.save()
            return redirect("recipe", recipe_name=recipe_name)
    else:
        review_form = ReviewForm()
    
    my_profile = None
    if request.user.is_authenticated:
        my_profile = Profile.objects.get(user=request.user)
    
    reviews = Review.objects.filter(recipe=recipe)
    profiles = Profile.objects.all()
    
    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()
    
    reviews_data = list(reviews.values('rating', 'description', 'user__username'))  # Serializing the reviews

    # Calculate rating distribution for this recipe
    rating_counts = reviews.values('rating').annotate(count=Count('rating'))
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    total_reviews = reviews.count()
    for rating in rating_counts:
        rating_distribution[str(rating['rating'])] = (rating['count'] / total_reviews) * 100

    return render(request, "foodhub/recipe.html", {
        "recipe": recipe,
        "categories": Recipe.CATEGORY_CHOICES,
        "featured_categories": Recipe.CATEGORY_CHOICES[:6],
        "ingredients": Ingredient.objects.filter(recipe=recipe),
        "steps": Step.objects.filter(recipe=recipe),
        "allergens": Allergen.objects.filter(recipe=recipe),
        "average_rating": average_rating,
        "user_reviewed": user_reviewed,
        "my_profile": my_profile,
        "profiles": profiles,
        "reviews": reviews,
        "reviews_data": json.dumps(reviews_data, cls=DjangoJSONEncoder),  
        "rating_distribution": rating_distribution,
        "review_form": review_form
    })

def rating_distribution(request, recipe_id):
    reviews = Review.objects.filter(recipe_id=recipe_id)
    rating_counts = reviews.values('rating').annotate(count=Count('rating'))
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    total_reviews = reviews.count()
    
    for rating in rating_counts:
        rating_distribution[str(rating['rating'])] = (rating['count'] / total_reviews) * 100
    
    return JsonResponse(rating_distribution)

def edit_recipe(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    if request.method == "POST":
        form = NewRecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            updated_recipe_name = form.cleaned_data['name']
            form.save()
            return redirect('recipe', recipe_name=updated_recipe_name)
    else:
        form = NewRecipeForm(instance=recipe)

    return render(request, "foodhub/edit_recipe.html", {
        "recipe": recipe,
        "form": form
    })

@csrf_exempt  
@login_required(login_url='/login_view')
def like_recipe(request, id):
    user = request.user
    recipe = Recipe.objects.get(id=id)
    liked = False
    if user not in recipe.likes.all():
        recipe.likes.add(user)
        liked = True
    else:
        recipe.likes.remove(user)   

    recipe.save()
    return JsonResponse({"liked": liked, "like_count": recipe.likes.count()})

@csrf_exempt  
@login_required(login_url='/login_view')
def follow(request, id):
    user = request.user
    profile = Profile.objects.get(id=id)
    followed = False
    if user not in profile.followers.all():
        profile.followers.add(user)
        followed = True
    else:
        profile.followers.remove(user)   

    profile.save()
    return JsonResponse({"followed": followed, "followers_count": profile.followers.count()})

@login_required(login_url='/login_view')
def create_review(request, recipe_name):
    if request.method == "POST":
        recipe = Recipe.objects.get(name=recipe_name)
        description = request.POST["description"]
        rating = request.POST["rating"]
        if len(description) != 0:
            user = request.user
            recipe = recipe
            description = description
            rating = rating
            review = Review.objects.create(user=user, recipe=recipe, description=description, rating=rating)
            review.save()
            return HttpResponseRedirect(reverse("recipe", args=[recipe_name]))

def categories(request):
    category_dict = {}

    # Get all categories that have at least one associated recipe
    categories_with_recipes = [
        category for category in Recipe.CATEGORY_CHOICES 
        if Recipe.objects.filter(category=category[0]).exists()
    ]

    for category in categories_with_recipes:
        first_letter = category[1][0].upper()  # Get the first letter of the category name and convert to uppercase
        if first_letter not in category_dict:
            category_dict[first_letter] = []
        category_recipes = Recipe.objects.filter(category=category[0])
        if category_recipes.exists():
            random_recipe = random.choice(category_recipes)
            category_dict[first_letter].append((category[0], category[1], random_recipe.image.url))
    
    # Sort categories within each letter group
    for letter in category_dict:
        category_dict[letter] = sorted(category_dict[letter], key=lambda x: x[1].lower())
    
    # Sort the dictionary items by keys
    sorted_category_dict = dict(sorted(category_dict.items()))

    query = request.GET.get('query')
    if query:
        query = query.lower() 
        filtered_categories = {}
        for letter, categories in sorted_category_dict.items():
            filtered_categories[letter] = [
                category for category in categories if query in category[1].lower()
            ]
        sorted_category_dict = filtered_categories
    else:
        query = ""
    
    return render(request, "foodhub/categories.html", {
        "category_dict": sorted_category_dict,
        "featured_categories": categories_with_recipes[:6],
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  
        "query": query,
        "categories_count": len(categories_with_recipes)
    })

def category(request, category):
    recipes = Recipe.objects.filter(category=category)
    header_recipe = None
    if recipes:
        header_recipe = random.choice(recipes)
    return render(request, "foodhub/category.html", {
        "categories": Recipe.CATEGORY_CHOICES,
        "featured_categories": Recipe.CATEGORY_CHOICES[:6],
        "recipes": recipes,
        "category": category,
        "header_recipe": header_recipe
    })

def ingredients(request):
    grouped_ingredients = Ingredient.objects.group_by_ingredient_name()

    ingredient_dict = {}

    for ingredient in grouped_ingredients:
        name = ingredient['lower_name'].title()
        first_letter = name[0].upper() if name else ''

        if first_letter not in ingredient_dict:
            ingredient_dict[first_letter] = []

        ingredient_dict[first_letter].append(name)
        
    for letter in ingredient_dict:
        ingredient_dict[letter] = sorted(ingredient_dict[letter])

    sorted_ingredients = dict(sorted(ingredient_dict.items()))

    query = request.GET.get('query')
    if query:
        query = query.lower()
        filtered_ingredients = {}
        for letter, ingredients in sorted_ingredients.items():
            filtered_ingredients[letter] = [
                ingredient for ingredient in ingredients if query in ingredient.lower()
            ]
        sorted_ingredients = filtered_ingredients
    else:
        query = ""

    return render(request, "foodhub/ingredients.html", {
        "grouped_ingredients":grouped_ingredients,
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  
        "sorted_ingredients": sorted_ingredients,
        "query": query,
        "ingredients_count": len(grouped_ingredients)
    })

def ingredient(request, ingredient):
    # Decode url-encoded ingredient name
    decoded_ingredient = unquote(ingredient)
    
    # Filter ingredients by the given name (case-insensitive)
    matched_ingredients = Ingredient.objects.filter(name__iexact=decoded_ingredient)
    
    # Get the recipes related to the matched ingredients using the related_name: recipe_ingredient in Ingredient model
    recipes = Recipe.objects.filter(recipe_ingredient__in=matched_ingredients).distinct()

    return render(request, "foodhub/ingredient.html", {
        "ingredient": decoded_ingredient,
        "recipes": recipes,
    })


def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    profile_recipes = Recipe.objects.filter(user=user)
    featured_recipe = profile.featured_recipe
    average_rating = Review.average_rating(featured_recipe) if featured_recipe else 0

    # Filter and calculate average ratings for popular recipes with reviews
    popular_recipes_with_ratings = [
        {
            "recipe": recipe,
            "average_rating": Review.average_rating(recipe)
        }
        for recipe in profile_recipes if Review.objects.filter(recipe=recipe).exists()
    ]
    # Sort by average rating and select top 3
    popular_recipes_with_ratings.sort(key=lambda x: x["average_rating"], reverse=True)
    popular_recipes_with_ratings = popular_recipes_with_ratings[:3]

    if request.method == "POST":
        if 'profile_image' in request.FILES:
            profile.image = request.FILES['profile_image']
            profile.save()
            return redirect('profile', username=username)

        new_featured_recipe_id = request.POST.get('new_featured_recipe')
        if new_featured_recipe_id:
            featured_recipe = Recipe.objects.get(id=new_featured_recipe_id)
            profile.featured_recipe = featured_recipe
            profile.save()
            return redirect('profile', username=username)

    if not featured_recipe and profile_recipes:
        featured_recipe = profile_recipes.first()

    return render(request, "foodhub/profile.html", {
        "user": user,
        "profile": profile,
        "profile_recipes": profile_recipes,
        "featured_recipe": featured_recipe,
        "average_rating": average_rating,
        "featured_categories": Recipe.CATEGORY_CHOICES[:6],
        "popular_recipes_with_ratings": popular_recipes_with_ratings
    })

@csrf_exempt
@login_required(login_url='/login')
def edit_bio(request):
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        profile = Profile.objects.get(user=request.user)
        profile.bio = new_bio
        profile.save()
        return redirect('profile', username=request.user.username)
    return redirect('profile', username=request.user.username)

@csrf_exempt
@login_required(login_url="/login")
def profile_allergen(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        selected_allergens = request.POST.getlist("allergens")
        allergens = Allergen.objects.filter(name__in=selected_allergens)
        profile.allergens.set(allergens)
        profile.save()
        messages.success(request, 'Allergen information updated successfully.')

    user_allergen_names = profile.allergens.values_list("name", flat=True)
    
    context = {
        "user": user,
        "profile": profile,
        "user_allergen_names": user_allergen_names,
    }
    return render(request, "foodhub/profile_allergen.html", context)

        
def edit_profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile.save()
    else:
        form = ProfileForm(instance=profile)
    return render(request, "foodhub/edit_profile.html", {
        "profile": profile,
        "form": form
    })

@login_required(login_url='/login')
def create_mealplan(request):
    all_recipes = Recipe.objects.all()
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            date = form.cleaned_data["date"]
            recipes_ids = request.POST.getlist("recipes")
            user = request.user

            mealplan = MealPlan.objects.create(name=name, description=description, date=date, user=user)
            mealplan.recipes.set(recipes_ids)
            mealplan.save()
            
            return render(request, "foodhub/create_mealplan.html", {
                "all_recipes": all_recipes,
                "form": form,
                "message": f"Mealplan for {mealplan.date} created"
            })
    else:
        form = MealPlanForm()

    return render(request, "foodhub/create_mealplan.html", {
        "form": form,
        "all_recipes": all_recipes
    })

@login_required(login_url='/login')
def edit_mealplan(request, date):
    try:
        mealplan = MealPlan.objects.get(date=date, user=request.user)
    except MealPlan.DoesNotExist:
        return JsonResponse({"error": "Meal plan not found"}, status=404)

    all_recipes = Recipe.objects.all()
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            mealplan.name = form.cleaned_data["name"]
            mealplan.description = form.cleaned_data["description"]
            mealplan.date = form.cleaned_data["date"]
            recipes_ids = request.POST.getlist("recipes")

            mealplan.recipes.set(recipes_ids)
            mealplan.save()

            return render(request, "foodhub/create_mealplan.html", {
                "all_recipes": all_recipes,
                "form": form,
                "message": f"Mealplan for {mealplan.date} updated"
            })
    else:
        form = MealPlanForm(initial={
            "name": mealplan.name,
            "description": mealplan.description,
            "date": mealplan.date,
        })

    return render(request, "foodhub/edit_mealplan.html", {
        "form": form,
        "all_recipes": all_recipes,
        "selected_recipes": mealplan.recipes.all(),
        "mealplan": mealplan,
    })
    
@login_required(login_url='/login')
def get_mealplan_by_date(request, date):
    if request.method == 'GET':
        try:
            mealplan = MealPlan.objects.get(date=date, user=request.user)
            recipes = mealplan.recipes.all()
            mealplan_data = {
                "mealplan": {
                    "name": mealplan.name,
                    "description": mealplan.description,
                    "date": mealplan.date
                },
                "recipes": []
            }

            for recipe in recipes:
                recipe_data = forms.model_to_dict(recipe, fields=['name', 'image', 'category', 'description'])
                recipe_data['image'] = recipe.image.url if recipe.image else None

                # Retrieve ingredients for the current recipe
                ingredients = Ingredient.objects.filter(recipe=recipe)
                recipe_data['ingredients'] = [{
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit_of_measurement
                } for ingredient in ingredients]

                # Retrieve steps for the current recipe
                steps = Step.objects.filter(recipe=recipe)
                recipe_data['steps'] = [{
                    "description": step.description,
                    "image": step.image.url if step.image else None,
                    "video": step.video.url if step.video else None
                } for step in steps]

                mealplan_data['recipes'].append(recipe_data)


            return JsonResponse(mealplan_data)
        except MealPlan.DoesNotExist:
            return JsonResponse({"mealplan": None})

@login_required(login_url='/login')       
def upcoming_mealplans(request, date):
    if request.method == "GET":
        try:
            upcoming_mealplans = MealPlan.objects.filter(date__gt=date, user=request.user).order_by('date')
            upcoming_mealplans_data = []
            for mealplan in upcoming_mealplans:
                mealplan_data = {
                    "name": mealplan.name,
                    "date": mealplan.date.strftime('%m-%d-%Y')
                }
                upcoming_mealplans_data.append(mealplan_data)
            return JsonResponse(upcoming_mealplans_data, safe=False)
        except MealPlan.DoesNotExist:
            return JsonResponse({"error": "No meal plans found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)    
        
def recipe_recommender(request):
    categories = [
        category for category in Recipe.CATEGORY_CHOICES 
        if Recipe.objects.filter(category=category[0]).exists()
    ]
    durations = Recipe.DURATION_CHOICES
    difficulty = Recipe.DIFFICULTY_CHOICES
    cost = Recipe.COST_CHOICES

    filters = {
        'category': request.GET.get('category'),
        'duration': request.GET.get('duration'),
        'difficulty': request.GET.get('difficulty'),
        'cost': request.GET.get('cost')
    }

    filters = {key: value for key, value in filters.items() if value}

    user_allergens = []  # Initialize user_allergens

    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
        user_allergens = user_profile.allergens.all()

    include_allergens = request.GET.get('include_allergens', 'no') == 'yes'

    def exclude_allergens(queryset, user_allergens):  # Pass user_allergens as argument
        if not include_allergens:
            for allergen in user_allergens:
                queryset = queryset.exclude(allergens=allergen)
        return queryset

    def get_filtered_recipes(filters):
        filtered_recipes = Recipe.objects.filter(**filters)
        filtered_recipes = exclude_allergens(filtered_recipes, user_allergens)  # Pass user_allergens
        return filtered_recipes

    recipe = None
    matched_filters = []

    # Prioritize category as most important filter
    if 'category' in filters:
        filtered_recipes = get_filtered_recipes({'category': filters['category']})
        if filtered_recipes.exists():
            recipe = filtered_recipes.order_by('?').first()
            matched_filters = ['category']
        else:
            # If no recipe found for the exact category, try relaxing other filters
            relaxed_filters = {key: value for key, value in filters.items() if key != 'category'}
            filtered_recipes = get_filtered_recipes(relaxed_filters)
            if filtered_recipes.exists():
                recipe = filtered_recipes.order_by('?').first()
                matched_filters = list(relaxed_filters.keys())

    # If still no recipe found, fallback to random selection
    if recipe is None:
        recipe = Recipe.objects.order_by('?').first()

    # Track which filters actually matched for the final recipe
    for key in filters.keys():
        if getattr(recipe, key, None) == filters[key]:
            matched_filters.append(key)

    # Determine if recipe allergens match user allergens
    recipe_allergens_match_user = all(allergen in user_allergens for allergen in recipe.allergens.all())

    return render(request, "foodhub/recipe_recommender.html", {
        "categories": categories,
        "durations": durations,
        "difficulty": difficulty,
        "cost": cost,
        "recipe": recipe,
        "test_category": filters.get('category'),
        "test_duration": filters.get('duration'),
        "test_difficulty": filters.get('difficulty'),
        "test_cost": filters.get('cost'),
        "matched_filters": matched_filters,
        "user_allergens": user_allergens,
        "include_allergens": include_allergens,
        "recipe_allergens": recipe.allergens.all(),
        "recipe_allergens_match_user": recipe_allergens_match_user
    })

def add_ingredients_to_list(request, recipe_name):
    recipe = Recipe.objects.get(name=recipe_name)
    ingredients = Ingredient.objects.filter(recipe=recipe)
    if request.method == 'POST':
        shopping_list = ShoppingList.objects.get(user=request.user)
        shopping_list.ingredients.add(*ingredients)
        return redirect('my_shopping_list')

@login_required(login_url='/login')
def my_shopping_list(request):
    shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
    ingredients = shopping_list.ingredients.select_related('recipe').order_by('recipe__name', 'name')

    ingredient_dict = defaultdict(list)

    for ingredient in ingredients:
        ingredient_dict[ingredient.recipe.name].append(ingredient)

    if request.method == 'POST':
        delete_recipe_name = request.POST.get('recipe_name')
        
        if delete_recipe_name:
            ingredients_to_remove = shopping_list.ingredients.filter(recipe__name=delete_recipe_name)
            for ingredient in ingredients_to_remove:
                shopping_list.ingredients.remove(ingredient)
            return redirect('my_shopping_list')

    return render(request, "foodhub/my_shopping_list.html", {
        "shopping_list": shopping_list,
        "ingredients": dict(ingredient_dict),
        "ingredient_count": len(ingredients),
    })

def practice(request):
    recipes = Recipe.objects.annotate(review_count=Count('ratings', distinct=True),avg_rating=Avg(
        'ratings__rating')).filter(review_count__gt=0).order_by('-avg_rating', '-review_count')[:10]

    return render(request, "foodhub/practice.html", {
        "recipes": recipes
    })
