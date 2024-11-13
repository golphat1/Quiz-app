#!/usr/bin/env python3

# Import necessary Django models and modules
from django.db import models
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from smart_open import open  # Handles opening files from various sources, including S3
import io  # Allows in-memory byte handling

# Category model: Represents a quiz category with a name
class Category(models.Model):
    name = models.CharField(max_length=15)  # Category name with max length of 15 characters

    class Meta:
        verbose_name_plural = 'Categories'  # Plural name in the Django admin

    def __str__(self):
        return self.name  # Returns the category name as a string


# Quiz model: Stores quiz details and handles uploading quiz files
class Quiz(models.Model):
    title = models.CharField(max_length=255)  # Quiz title
    description = models.TextField()  # Description of the quiz
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Link to category, deleted with category
    quiz_file = models.FileField(upload_to='quiz/')  # File field for uploading quiz file (Excel)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set at quiz creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated when quiz is modified

    class Meta:
        verbose_name_plural = 'Quizzes'  # Plural name in Django admin

    def __str__(self):
        return self.title  # Returns quiz title as a string

    # Override the save method to trigger Excel file import upon saving
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the base class save method
        if self.quiz_file:
            self.import_quiz_from_excel()  # Import quiz data if file is provided

    # Method to import quiz questions and choices from an Excel file
    def import_quiz_from_excel(self):
        # Use self.quiz_file.url to access the S3 file URL
        s3_url = self.quiz_file.url

        # Open the Excel file from S3 using smart_open
        with open(s3_url, 'rb') as file:
            # Load Excel file content into a pandas DataFrame
            df = pd.read_excel(io.BytesIO(file.read()))

        # Iterate over each row in the DataFrame to extract question and choices
        for index, row in df.iterrows():
            question_text = row['Question']  # Question text
            choice1 = row['A']  # Option A
            choice2 = row['B']  # Option B
            choice3 = row['C']  # Option C
            choice4 = row['D']  # Option D
            correct_answer = row['Answer']  # Correct answer

            # Create or retrieve Question object
            question = Question.objects.get_or_create(quiz=self, text=question_text)

            # Create Choice objects for each option
            Choice.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
            Choice.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
            Choice.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
            Choice.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')


# Question model: Represents a single question in a quiz
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # Linked quiz, deleted with quiz
    text = models.TextField()  # Question text

    def __str__(self):
        return self.text[:50]  # Returns first 50 chars of question text


# Choice model: Represents an answer choice for a question
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Linked question, deleted with question
    text = models.CharField(max_length=255)  # Choice text
    is_correct = models.BooleanField(default=False)  # Indicates if this choice is correct

    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"  # Returns a short description of the choice


# QuizSubmission model: Tracks each user's submission and score for a quiz
class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who submitted the quiz
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # Quiz being submitted
    score = models.IntegerField()  # Score achieved by the user
    submitted_at = models.DateTimeField(auto_now_add=True)  # Submission timestamp

    def __str__(self):
        return f"{self.user}, {self.quiz.title}"  # Returns user and quiz info


# UserRank model: Tracks the rank and total score of each user for leaderboard
class UserRank(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Unique link to a user
    rank = models.IntegerField(null=True, blank=True)  # User rank
    total_score = models.IntegerField(null=True, blank=True)  # Total score across all quizzes

    def __str__(self):
        return f"{self.rank}, {self.user.username}"  # Returns rank and username

    # Signal receiver to update leaderboard whenever a QuizSubmission is created
    @receiver(post_save, sender=QuizSubmission)
    def update_leaderboard(sender, instance, created, **kwargs):
        if created:
            update_leaderboard()  # Calls the function to update leaderboard


# Function to update the leaderboard based on user scores
def update_leaderboard():
    # Aggregate total scores for all users, ordered by score descending
    user_scores = (QuizSubmission.objects.values('user')
                   .annotate(total_score=Sum('score'))
                   .order_by('-total_score'))

    # Update each user's rank based on score
    rank = 1  # Starting rank
    for entry in user_scores:
        user_id = entry['user']
        total_score = entry['total_score']

        # Update or create UserRank for each user
        user_rank, created = UserRank.objects.get_or_create(user_id=user_id)
        user_rank.rank = rank
        user_rank.total_score = total_score
        user_rank.save()

        rank += 1  # Increment rank for next user
