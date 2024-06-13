document.addEventListener("DOMContentLoaded", function() {
    // Function to update stars based on rating
    function updateStars(rating, stars) {
        // Round the average rating to the nearest 0.5
        var roundedRating = Math.round(rating * 2) / 2;

        // Loop through the stars and set them based on the rounded rating
        stars.forEach(function(star, index) {
            star.classList.remove('fa-solid', 'fa-star-half-stroke');
            star.classList.add('fa-regular');
            
            if (index < Math.floor(roundedRating)) {
                star.classList.add('fa-solid');
                star.classList.remove('fa-regular');
            } else if (index == Math.floor(roundedRating) && roundedRating % 1 !== 0) {
                // Display half star if roundedRating is not an integer
                star.classList.add('fa-solid', 'fa-star-half-stroke');
                star.classList.remove('fa-regular');
            }
        });
    }

    // Get the average rating from .average-review
    var averageReviewElement = document.querySelector('.average-review');
    if (averageReviewElement) {
        var averageRating = parseFloat(averageReviewElement.textContent);
        var stars = document.querySelectorAll('.fa-star.average-review-star');
        updateStars(averageRating, stars);
    }

    // Get the average rating from .featured-rating
    var featuredRatingElement = document.querySelector('.featured-rating');
    if (featuredRatingElement) {
        var featuredRating = parseFloat(featuredRatingElement.textContent);
        var stars = document.querySelectorAll('.fa-star.featured-rating-star');
        updateStars(featuredRating, stars);
    }

    // Loop through all elements with class 'profile-popular-card' and update their stars
    document.querySelectorAll('.profile-popular-card').forEach(function(card) {
        var averageReviewElement = card.querySelector('.popular-review');
        if (averageReviewElement) {
            var averageRating = parseFloat(averageReviewElement.textContent);
            var stars = card.querySelectorAll('.fa-star.popular-review-star');
            updateStars(averageRating, stars);
        }
    });
});

const stars = document.querySelectorAll('.rating input[type="radio"]');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                stars.forEach(s => {
                    if (s.id <= star.id) {
                        s.parentNode.classList.add('selected');
                    } else {
                        s.parentNode.classList.remove('selected');
                    }
                });
            });
        });

const radioButtons = document.querySelectorAll('#filter-form input[type="radio"]');
radioButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Submit the form when a radio button is clicked
        document.getElementById('filter-form').submit();
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // for sort type
    const sortDropdown = document.querySelector('.sort-dropdown');
    const sortContent = document.querySelector('.sort-content');
    const form = document.querySelector('.sort-form');
    const radioButtons = form.querySelectorAll('input[type="radio"]');
    const sortTypeText = document.querySelector('.sort-type'); // Updated selector

    // for ratings
    const ratingDropdown = document.querySelector('.filter-rating'); 
    const ratingContent = document.querySelector('.rating-content');

    // Toggle dropdown visibility when the dropdown is clicked
    sortDropdown.addEventListener('click', function(event) {
        sortContent.style.display = sortContent.style.display === 'block' ? 'none' : 'block';
        event.stopPropagation(); // Prevent the click event from bubbling up to the window
    });    

    const submitForm = () => {
        form.submit(); 
    };

    // Function to update the "Sort By" text based on sort_type
    const updateSortByText = (sortType) => {
        if (sortType === 'name') {
            sortTypeText.textContent = 'Sort by: Default';
        } else if (sortType === '-name') {
            sortTypeText.textContent = 'Sort by: Z-A';
        } else if (sortType === 'date') {
            sortTypeText.textContent = 'Sort by: Oldest-Newest';
        } else if (sortType === '-date') {
            sortTypeText.textContent = 'Sort by: Newest-Oldest';
        }
    };

    radioButtons.forEach(radioButton => {
        radioButton.addEventListener('change', function() {
            submitForm(); 
            updateSortByText(this.value); // Call the function to update the "Sort By" text
        }); 
    });

    ratingDropdown.addEventListener('click', function(event) {
        ratingContent.style.display = ratingContent.style.display === 'block' ? 'none' : 'block';

        // Close sort dropdown if open
        if (sortContent.style.display === 'block') {
            sortContent.style.display = 'none';
        }

        event.stopPropagation(); // Prevent the click event from bubbling up to the window
    });

    window.addEventListener('click', function(event) {
        // Close sort dropdown if open
        if (sortContent.style.display === 'block') {
            sortContent.style.display = 'none';
        }

        // Close rating dropdown if open
        if (ratingContent.style.display === 'block') {
            ratingContent.style.display = 'none';
        }
    });

    // Call the function to initially update the "Sort By" text based on the current sort type
    const initialSortType = document.querySelector('input[name="sort"]:checked').value;
    updateSortByText(initialSortType);
});


document.addEventListener("DOMContentLoaded", function() {
    var reviewCountLink = document.querySelector('.review-count a');

    if(reviewCountLink) {
        reviewCountLink.addEventListener('click', function(event) {
            event.preventDefault();
            var reviewsSection = document.querySelector('.review-list');
            reviewsSection.scrollIntoView({ behavior: 'smooth' });
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const recipeCardContainer = document.querySelector(".recipe-card-container");
    const communitySection = document.querySelector(".community");

    function checkScroll() {
        const windowHeight = window.innerHeight;
        const recipeCardContainerTop = recipeCardContainer.getBoundingClientRect().top;
        const communitySectionTop = communitySection.getBoundingClientRect().top;

        if (recipeCardContainerTop < windowHeight * 0.75) {
            recipeCardContainer.classList.add("visible");
        }

        if (communitySectionTop < windowHeight * 0.80) {
            communitySection.classList.add("visible-community");
        }
    }

    window.addEventListener("scroll", checkScroll);
    checkScroll(); // Check initially in case the elements are already visible on page load
});

document.addEventListener('DOMContentLoaded', function() {
    const toggleSidebarButton = document.getElementById('toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    toggleSidebarButton.addEventListener('click', function() {
        sidebar.classList.add('show'); // Toggle the 'show' class on the sidebar
    });

    window.addEventListener('click', function(event) {
        if (!sidebar.contains(event.target) && !toggleSidebarButton.contains(event.target)) {
            sidebar.classList.remove('show');
        }
    });
});

document.querySelectorAll('.like-btn').forEach(btn => {
    btn.onclick = function() {
        like(btn);
    }
});

function like(element) {
    fetch(`/like_recipe/${element.dataset.id}`)
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            element.classList.add('liked');
            showNotification("Recipe liked!");
        } else {
            element.classList.remove('liked');
            showNotification("Like removed.");
        }
    })
    .catch(error => console.error("Error:", error));
}

document.querySelectorAll('.follow-btn').forEach(btn => {
    btn.onclick = function() {
        follow(btn);
    }
});

function follow(element) {
    fetch(`/follow/${element.dataset.id}`)
    .then(response => response.json())
    .then(data => {
        if (data.followed) {
            element.classList.add('followed');
            element.innerHTML = "Unfollow";
            showNotification("Profile followed!");
        } else {
            element.classList.remove('followed');
            element.innerHTML = "Follow";
            showNotification("Profile Unfollowed.");
        }
        document.querySelector('#followers').innerHTML = "Followers: " + data.followers_count
    })
    .catch(error => console.error("Error:", error));
}

function showNotification(message) {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        document.body.appendChild(notification);
    }

    // Set the notification message
    notification.textContent = message;

    // Display the notification
    notification.style.display = 'block';

    // Hide the notification after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    const toggleAllergensBtn = document.getElementById('toggle-allergens-btn');
    toggleAllergensBtn.addEventListener('change', function () {
        this.form.submit();
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const toggleLikesBtn = document.getElementById('toggle-likes-btn');
    toggleLikesBtn.addEventListener('change', function () {
        this.form.submit();
    });
});


var selectedCategory = "{{ selected_category }}";
var selectedDuration = "{{ selected_duration }}";
var selectedCost = "{{ selected_cost }}";
var selectedDifficulty = "{{ selected_difficulty }}";

function updateSelectedOptions(fieldName, value) {
    if (fieldName === "category") {
        selectedCategory = value;
    } else if (fieldName === "duration") {
        selectedDuration = value;
    } else if (fieldName === "cost") {
        selectedCost = value;
    } else if (fieldName === "difficulty") {
        selectedDifficulty = value;
    }
}

// editing profile featured recipe 
document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.querySelector('.edit-featured');
    const editContainer = document.querySelector('.edit-recipes-container');

    // Function to toggle the visibility of the edit container
    function toggleEditContainer() {
        if (editContainer.style.bottom === '0px') {
            editContainer.style.bottom = '-600px';
        } else {
            editContainer.style.bottom = '0px';
        }
    }

    // Click event listener for the "Edit" button
    editButton.addEventListener('click', function(event) {
        event.stopPropagation(); // Prevent the click event from propagating to the document body
        toggleEditContainer();
    });

    // Click event listener for the document body to close the container when clicking outside of it
    document.body.addEventListener('click', function(event) {
        // Check if the clicked element is not within the edit container
        if (!editContainer.contains(event.target) && event.target !== editButton) {
            editContainer.style.bottom = '-600px';
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const recipeChoices = document.querySelectorAll('.recipe-choice');

    // Click event listener for recipe choices
    recipeChoices.forEach(function(choice) {
        choice.addEventListener('click', function() {
            const recipeId = choice.dataset.recipeId;
            document.getElementById('new-featured-recipe-input').value = recipeId;
            document.getElementById('edit-featured-recipe-form').submit();
        });
    });
});

// allergen checkbox function
document.addEventListener("DOMContentLoaded", function() {
    const allergens = document.querySelectorAll('.allergen-choice');
    allergens.forEach(allergen => {
        allergen.addEventListener('change', function() {
            document.getElementById('allergen-form').submit();
        });
    });
});

// choosing recipe image for create form
document.getElementById('image-container').addEventListener('click', function() {
    document.querySelector('.create-recipe-image input[type="file"]').click();
});

document.querySelector('.create-recipe-image input[type="file"]').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var selectedImage = document.getElementById('selected-image');
            var imageContainer = document.querySelector('.create-recipe-image');
            
            selectedImage.src = e.target.result;
            selectedImage.style.display = 'block';
            selectedImage.style.width = '100%';
            selectedImage.style.height = '100%';

            document.getElementById('image-placeholder').style.display = 'none';

            // Change border to solid
            imageContainer.style.border = 'solid 1px black';
        }
        reader.readAsDataURL(file);
    }
});

// adding media for recipe directions
document.getElementById('add-step-image').addEventListener('click', function() {
    document.getElementById('image-upload').click();
});

// Function to trigger video upload when video icon is clicked
document.getElementById('add-step-video').addEventListener('click', function() {
    document.getElementById('video-upload').click();
});


// profile image editing
document.getElementById('profile-image').addEventListener('click', function() {
    document.getElementById('profile-image-input').click();
});

document.getElementById('profile-image-input').addEventListener('change', function() {
    document.getElementById('submit-profile-image').click();
});


// profile bio editing
function showEditForm() {
    document.getElementById('bio-text').style.display = 'none';
    document.querySelector('.edit-bio').style.display = 'none';
    document.getElementById('edit-bio-form').style.display = 'block';
}

function hideEditForm() {
    document.getElementById('bio-text').style.display = 'block';
    document.querySelector('.edit-bio').style.display = 'block';
    document.getElementById('edit-bio-form').style.display = 'none';
}


document.addEventListener("DOMContentLoaded", function() {
    const signUpButton = document.getElementById("signUpButton");
    const loginButton = document.getElementById("loginButton");
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");
    const toggleToRegister = document.getElementById("toggleToRegister");
    const toggleToLogin = document.getElementById("toggleToLogin");

    signUpButton.addEventListener("click", function(event) {
        event.preventDefault();
        loginForm.classList.remove("form-visible");
        loginForm.classList.add("form-hidden");
        setTimeout(() => {
            registerForm.classList.remove("form-hidden");
            registerForm.classList.add("form-visible");
            toggleToRegister.style.display = "none";
            signUpButton.style.display = "none";
            toggleToLogin.style.display = "block";
            loginButton.style.display = "block";
        }, 500); // Match the transition duration
    });

    loginButton.addEventListener("click", function(event) {
        event.preventDefault();
        registerForm.classList.remove("form-visible");
        registerForm.classList.add("form-hidden");
        setTimeout(() => {
            loginForm.classList.remove("form-hidden");
            loginForm.classList.add("form-visible");
            toggleToRegister.style.display = "block";
            signUpButton.style.display = "block";
            toggleToLogin.style.display = "none";
            loginButton.style.display = "none";
        }, 500); // Match the transition duration
    });
});


// date picker for choosing date on calendar for mealplans
document.addEventListener('DOMContentLoaded', function() {
    var dateInput = document.getElementById('id_date_input');
    var hiddenDateInput = document.getElementById('id_date');
    
    // Set initial value of hidden input to match date_input
    hiddenDateInput.value = dateInput.value + 'T00:00';

    // Update hidden input when date_input changes
    dateInput.addEventListener('change', function() {
        hiddenDateInput.value = this.value + 'T00:00';
    });
});