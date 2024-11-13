#!/usr/bin/env python3

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Profile
from quiz.models import QuizSubmission

# Create your views here.

def leaderboard_view(request):
    """
    View to display the leaderboard, showing the top 10 users by score.
    """
    leaderboard = Profile.objects.order_by('-score')[:10]  # Fetch top 10 users by score

    context = {
        'leaderboard': leaderboard
    }
    return render(request, 'account/leaderboard.html', context)


def home(request):
    """
    View for the home page, displaying the top 3 users from the leaderboard.
    """
    top_users = Profile.objects.order_by('-score')[:3]  # Fetch top 3 users by score

    context = {
        'top_users': top_users,
    }
    return render(request, 'account/home.html', context)


def register(request):
    """
    User registration view. If the user is authenticated, redirects to the profile page.
    Checks if email and username are unique before creating a new user and profile.
    """
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Ensure email is unique
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used. Try to Login.")
                return redirect('register')

            # Ensure username is unique
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken.")
                return redirect('register')
            
            else:
                # Create a new user and profile
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Log in the new user and redirect to their profile page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Create a profile associated with the new user
                new_profile = Profile.objects.create(user=user)
                new_profile.save()
                return redirect('profile', username)
        else:
            messages.info(request, "Password Not Matching.")
            return redirect('register')

    return render(request, "register.html")


@login_required
def profile(request, username):
    """
    Profile view displaying user information and their quiz submissions.
    """
    user_object2 = get_object_or_404(User, username=username)
    user_profile2 = get_object_or_404(Profile, user=user_object2)

    # Retrieve quiz submissions for the user
    submissions = QuizSubmission.objects.filter(user=user_object2)

    context = {"user_profile2": user_profile2, "submissions": submissions}
    return render(request, "profile.html", context)


@login_required
def editProfile(request):
    """
    View for editing the profile, including username, email, and personal information.
    """
    user_object = request.user
    user_profile = request.user.profile

    if request.method == "POST":
        # Update profile image if provided
        if request.FILES.get('profile_img'):
            user_profile.profile_img = request.FILES.get('profile_img')
            user_profile.save()

        # Check if email is unique before updating
        email = request.POST.get('email')
        if email and not User.objects.filter(email=email).exclude(id=user_object.id).exists():
            user_object.email = email
            user_object.save()
        elif email:
            messages.info(request, "Email Already Used, Choose a different one!")
            return redirect('edit_profile')

        # Check if username is unique before updating
        username = request.POST.get('username')
        if username and not User.objects.filter(username=username).exclude(id=user_object.id).exists():
            user_object.username = username
            user_object.save()
        elif username:
            messages.info(request, "Username Already Taken, Choose a unique one!")
            return redirect('edit_profile')

        # Update first name, last name, location, bio, and gender
        user_object.first_name = request.POST.get('firstname')
        user_object.last_name = request.POST.get('lastname')
        user_object.save()

        user_profile.location = request.POST.get('location')
        user_profile.gender = request.POST.get('gender')
        user_profile.bio = request.POST.get('bio')
        user_profile.save()

        return redirect('profile', user_object.username)

    context = {"user_profile": user_profile}
    return render(request, 'profile-edit.html', context)


@login_required
def deleteProfile(request):
    """
    View to delete the user profile and associated account.
    """
    user_object = request.user
    user_profile = request.user.profile

    if request.method == "POST":
        user_profile.delete()
        user_object.delete()
        return redirect('logout')

    return render(request, 'confirm.html')


def login(request):
    """
    User login view. If the user is already authenticated, redirects to the profile page.
    """
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('profile', username)
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')

    return render(request, "login.html")


@login_required
def logout(request):
    """
    User logout view, which logs out the user and redirects to the login page.
    """
    auth.logout(request)
    return redirect('login')
