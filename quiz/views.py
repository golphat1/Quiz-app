#!/usr/bin/env python3

from django.shortcuts import render, redirect, get_object_or_404  # For rendering templates and managing redirects
from django.contrib.auth.decorators import login_required  # To enforce login for specific views
from django.contrib.auth.models import User  # To handle user-related data
from account.models import Profile  # Import user Profile model
from .models import Quiz, Category  # Import Quiz and Category models for querying
from django.db.models import Q  # For complex query conditions in search
from quiz.models import QuizSubmission  # Import QuizSubmission model to handle quiz submission
from django.contrib import messages  # For displaying messages to users

# View for displaying all quizzes
@login_required  # Ensures that only logged-in users can access this view
def all_quiz_view(request):
    # Fetch all quizzes, ordering them by creation date (newest first)
    quizzes = Quiz.objects.order_by('-created_at')
    # Fetch all categories to display in the view
    categories = Category.objects.all()

    # Pass quizzes and categories to the template
    context = {"quizzes": quizzes, "categories": categories}
    return render(request, 'all-quiz.html', context)  # Render 'all-quiz.html' with context data


# View for searching quizzes by category or search term
@login_required  # Restrict access to logged-in users only
def search_view(request, category):
    # Search by search term from a search bar if it exists
    if request.GET.get('q') is not None:
        q = request.GET.get('q')  # Retrieve search term from GET request
        # Search for quizzes with title or description matching the term
        query = Q(title__icontains=q) | Q(description__icontains=q)
        quizzes = Quiz.objects.filter(query).order_by('-created_at')
    
    # Search by category if a valid category is provided
    elif category.strip():  # Check that category is not just whitespace
        quizzes = Quiz.objects.filter(category__name=category).order_by('-created_at')
    
    # If no search term or category, show all quizzes
    else:
        quizzes = Quiz.objects.order_by('-created_at')

    # Fetch all categories to include in the context for filter options
    categories = Category.objects.all()

    # Pass quizzes and categories to the template
    context = {"quizzes": quizzes, "categories": categories}
    return render(request, 'all-quiz.html', context)  # Render 'all-quiz.html' with context data


# View for displaying a specific quiz and handling quiz submission
@login_required  # Restrict access to logged-in users only
def quiz_view(request, quiz_id):
    # Fetch the quiz object or return a 404 if it doesn't exist
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Handle quiz submission when the form is submitted
    if request.method == "POST":
        # Retrieve the score from the form submission, defaulting to 0 if not provided
        score = int(request.POST.get('score', 0))

        # Create and save a new QuizSubmission object for the user
        submission = QuizSubmission(user=request.user, quiz=quiz, score=score)
        submission.save()  # Save the submission to the database

        # Redirect to the quiz result view, passing the submission ID
        return redirect('quiz_result', submission_id=submission.id)

    # Render 'quiz.html' with the quiz object in the context if GET request
    return render(request, 'quiz.html', {'quiz': quiz})


# View for displaying the result of a quiz submission
@login_required  # Restrict access to logged-in users only
def quiz_result_view(request, submission_id):
    # Fetch the specific submission by ID for the logged-in user, or return 404 if not found
    submission = get_object_or_404(QuizSubmission, pk=submission_id, user=request.user)
    
    # Pass the submission to the template for displaying results
    context = {'submission': submission}
    return render(request, 'quiz-result.html', context)  # Render 'quiz-result.html' with submission data
