from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Profile
from quiz.models import QuizSubmission

# Create your views here.

def home(request):
    """
    Home view that renders the homepage.
    """
    return render(request, 'home.html')

def leaderboard_view(request):
    """
    Display the leaderboard page.
    """
    return render(request, 'leaderboard.html')

def dashboard_view(request):
    """
    Render the dashboard page.
    """
    return render(request, 'dashboard.html')

def message_view(request, id):
    """
    Render a message page for a specific message ID.
    """
    return render(request, 'message.html', {'id': id})

def blogs_view(request):
    # Add your logic here for handling the blogs page
    # (e.g., fetch blog data, render a template)
    context = {
        'blogs': [],  # Replace with actual blog data if needed
    }
    return render(request, 'base/blogs.html', context)  # Adjust template path

def about_view(request):
    #  fetching data from the database,
    # processing it, and passing it to the template.
    context = {
        'about_text': 'This is the about page of my Django application.',
        # Add more context variables as needed
    }
    return render(request, 'base/about.html', context)

def blog_view(request, blog_id):
    # Add your logic here to retrieve and display a specific blog post based on the blog_id
    context = {
        'blog_id': blog_id,
        'blog_post': None,  # Replace with actual blog data
    }
    return render(request, 'base/blog_detail.html', context)  # Adjust template path

def contact_view(request):
    # Add your logic here for handling the contact page
    # (e.g., display a contact form, handle form submissions)
    context = {}  # Add context data as needed
    return render(request, 'base/contact.html', context)  # Adjust template path

def terms_conditions_view(request):
    # Add your logic here for handling the terms and conditions page
    # (e.g., display the terms and conditions text)
    context = {'terms_and_conditions': "Your terms and conditions text goes here"}  # Replace with actual content
    return render(request, 'base/terms_and_conditions.html', context)  # Adjust template path

def downloads_view(request):
    # Add your logic here for handling downloads page or functionality
    # (e.g., display a list of downloadable files, handle download requests)
    context = {}  # Add context data as needed
    return render(request, 'base/downloads.html', context)  # Adjust template path

def search_users_view(request):
    # Add your logic here for handling downloads page or functionality
    # (e.g., display a list of downloadable files, handle download requests)
    context = {}  # Add context data as needed
    return render(request, 'base/search_users.html', context)  # Adjust template path

def some_other_view(request):
    # Add your logic here for handling downloads page or functionality
    # (e.g., display a list of downloadable files, handle download requests)
    context = {}  # Add context data as needed
    return render(request, 'base/some_other.html', context)  # Adjust template path

def register(request):
    """
    Register a new user. If the user is already authenticated, redirects to their profile.
    Handles form submission for user registration with basic validations for unique email and username.
    """
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # Check for existing email
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used. Try to Login.")
                return redirect('register')
            # Check for existing username
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken.")
                return redirect('register')
            else:
                # Create and log in new user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Create profile for the new user
                Profile.objects.create(user=user)
                return redirect('profile', username)
        else:
            messages.info(request, "Password Not Matching.")
            return redirect('register')

    return render(request, "register.html")

@login_required
def profile(request, username):
    """
    Display user profile page. Shows user's profile and their quiz submissions.
    """
    user_object = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(Profile, user=user_object)
    submissions = QuizSubmission.objects.filter(user=user_object)

    context = {"user_profile": user_profile, "submissions": submissions}
    return render(request, "profile.html", context)

@login_required
def editProfile(request):
    """
    Edit the user's profile, including email, username, first/last name, location, bio, and profile image.
    Validates unique email and username to avoid duplication with other users.
    """
    user_object = request.user
    user_profile = user_object.profile

    if request.method == "POST":
        # Update profile image
        if request.FILES.get('profile_img'):
            user_profile.profile_img = request.FILES.get('profile_img')
            user_profile.save()

        # Update email with uniqueness check
        email = request.POST.get('email')
        if email:
            existing_user = User.objects.filter(email=email).exclude(id=user_object.id).first()
            if existing_user:
                messages.info(request, "Email Already Used, Choose a different one!")
                return redirect('edit_profile')
            user_object.email = email

        # Update username with uniqueness check
        username = request.POST.get('username')
        if username:
            existing_user = User.objects.filter(username=username).exclude(id=user_object.id).first()
            if existing_user:
                messages.info(request, "Username Already Taken, Choose a unique one!")
                return redirect('edit_profile')
            user_object.username = username

        # Update first and last names
        user_object.first_name = request.POST.get('firstname', user_object.first_name)
        user_object.last_name = request.POST.get('lastname', user_object.last_name)
        user_object.save()

        # Update additional profile information
        user_profile.location = request.POST.get('location', user_profile.location)
        user_profile.gender = request.POST.get('gender', user_profile.gender)
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.save()

        return redirect('profile', user_object.username)

    return render(request, 'profile-edit.html', {"user_profile": user_profile})

@login_required
def deleteProfile(request):
    """
    Deletes the user's profile and account upon confirmation.
    Redirects to the logout page after deletion.
    """
    if request.method == "POST":
        request.user.profile.delete()
        request.user.delete()
        return redirect('logout')

    return render(request, 'confirm.html')

def login(request):
    """
    Login user. If already authenticated, redirects to the user's profile.
    Handles form submission for login and authenticates credentials.
    """
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('profile', username)
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')

    return render(request, "login.html")

@login_required
def logout(request):
    """
    Logout the user and redirect to the login page.
    """
    auth.logout(request)
    return redirect('login')

def custom_404(request, exception):
    """
    Custom 404 error handler.
    Renders a custom 404 error page when a page is not found.
    """
    return render(request, '404.html', status=404)
