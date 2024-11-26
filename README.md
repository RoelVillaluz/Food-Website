# **Foodhub**

**Dynamic Recipe Website**

Foodhub is an innovative platform designed to allow users to explore, discover, and share recipes tailored to their dietary preferences, culinary skills, and allergens. Whether you're a seasoned chef or a beginner in the kitchen, Foodhub helps you find the perfect recipes that fit your needs.

https://github.com/user-attachments/assets/72092065-6707-418d-8dc6-aa496bbea958


## Authors

- **Roel Villaluz** - [@RoelVillaluz](https://github.com/RoelVillaluz)

## Features

- **Personalized Recipe Recommendations**: Get tailored recipe suggestions based on your unique preferences, dietary restrictions, and saved favorites.
  
- **Dietary Preferences and Allergens Management**: Users can easily manage their dietary preferences, including vegetarian, vegan, gluten-free, nut-free, and more, ensuring a safe and enjoyable cooking experience.
  
- **Advanced Search Filters**: Utilize powerful filters to find recipes by ingredients, cuisine type, dietary restrictions, cooking time, and difficulty level.
  
- **User Profile Management**: Create and manage a personalized user profile that includes a profile picture, bio, saved recipes, and preferred dietary settings.
  
- **Meal Planning**: Plan your meals with ease, saving time and effort while ensuring a balanced and delicious diet.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- SQLite (or your preferred database)

### Installation

1. Clone the repository:

 ```bash
 git clone https://github.com/RoelVillaluz/Foodhub.git
 cd Foodhub
  ```
 
2. Create a virtual environment and activate it:

  ```bash
 python -m venv env
 source env/Scripts/activate  # On Mac use `source env\bin\activate`
  ```


3. Install the required packages:
  ```bash
  pip install -r requirements.txt
  ```

4. Set up your database (e.g., SqLite, PostgreSQL) and update the settings.py with your database configuration.


5. Run the migrations:
  ```bash
  python manage.py runserver
  ```

6. Create a superuser to access the admin panel (Optional)
  ```bash
  python manage.py createsuperuser
  ```

7. Start the development server:
  ```bash
  python manage.py runserver
  ```

