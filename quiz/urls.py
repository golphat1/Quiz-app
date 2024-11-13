#!/usr/bin/env python3

from django.urls import path  
from . import views 

# Define URL patterns for the quiz app
urlpatterns = [
    # URL pattern for viewing all quizzes; maps to all_quiz_view in views
    path('all_quiz', views.all_quiz_view, name='all_quiz'),
    
    # URL pattern for searching quizzes by category; uses a string parameter "category"
    path('search/<str:category>', views.search_view, name='search'),
    
    # URL pattern for viewing a specific quiz; expects an integer "quiz_id" parameter
    path('<int:quiz_id>', views.quiz_view, name='quiz'),
    
    # URL pattern for viewing quiz results; expects an integer "submission_id" parameter
    path('<int:submission_id>/result/', views.quiz_result_view, name='quiz_result'),
]
