#!/usr/bin/env python3

from django.test import TestCase
from .models import Quiz, Question, Choice, Category  # Importing models for testing
import pandas as pd
import io  # For in-memory byte stream handling
from django.core.files.uploadedfile import SimpleUploadedFile  # Utility for testing file uploads
from unittest.mock import patch  # To mock dependencies
from django.contrib.auth.models import User
from django.urls import reverse  # For reversing URLs in tests

# Test case for the Quiz model and related functionality
class QuizModelTest(TestCase):
    # Setup method to prepare necessary objects for the tests
    def setUp(self):
        # Create a Category instance to associate with the Quiz
        self.category = Category.objects.create(name='AI')

        # Create an in-memory Excel file with questions and choices data
        self.excel_file = io.BytesIO()
        df = pd.DataFrame({
            'Question': ['What is 2+2?', 'What is 3+5?'],  # Questions
            'A': ['1', '2'],  # Choice A for each question
            'B': ['3', '4'],  # Choice B for each question
            'C': ['5', '8'],  # Choice C for each question
            'D': ['4', '9'],  # Choice D for each question
            'Answer': ['D', 'C']  # Correct answers
        })
        # Save DataFrame to the Excel file stream
        df.to_excel(self.excel_file, index=False, engine="openpyxl")
        self.excel_file.seek(0)  # Reset file pointer to the beginning

        # Upload Excel file using Django's SimpleUploadedFile utility for testing
        self.uploaded_file = SimpleUploadedFile('test_quiz.xlsx', self.excel_file.read(), content_type='application/vnd.ms-excel')

        # Create a Quiz instance and associate it with the uploaded file and category
        self.quiz = Quiz.objects.create(
            title='Quiz title', 
            description='Quiz desc', 
            category=self.category, 
            quiz_file=self.uploaded_file
        )

    # Test the functionality of importing quiz data from an Excel file
    @patch('quiz.models.pd.read_excel')  # Mock read_excel to avoid real file processing
    def test_import_quiz_from_excel(self, mock_read_excel):
        # Mocked data to simulate reading from an Excel file
        mock_df = pd.DataFrame({
            'Question': ['What is 2+2?', 'What is 3+5?'],
            'A': ['1', '2'],
            'B': ['3', '4'],
            'C': ['5', '8'],
            'D': ['4', '9'],
            'Answer': ['D', 'C']
        })

        # Set the mock to return the DataFrame when called
        mock_read_excel.return_value = mock_df

        # Save the quiz to trigger the import function
        self.quiz.save()

        # Check that two questions and eight choices (4 per question) are created
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Choice.objects.count(), 8)

        # Verify choices for each question
        question1 = Question.objects.get(text='What is 2+2?')
        question2 = Question.objects.get(text='What is 3+5?')

        # Assert that each question has exactly four choices
        self.assertEqual(Choice.objects.filter(question=question1).count(), 4)
        self.assertEqual(Choice.objects.filter(question=question2).count(), 4)

    # Test that the verbose name plural for Quiz model is 'Quizzes'
    def test_plural_quizzes(self):
        self.assertEqual(str(Quiz._meta.verbose_name_plural), 'Quizzes')


# Test case for the template displaying all quizzes
class AllQuizTemplateTest(TestCase):
    # Setup method to create user, categories, and quizzes for the test
    def setUp(self):
        # Create and login a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create two categories
        self.category1 = Category.objects.create(name='Science')
        self.category2 = Category.objects.create(name='English')

        # Create quizzes under each category
        self.quiz1 = Quiz.objects.create(title='Quiz 1', description='Desc 1', category=self.category1)
        self.quiz2 = Quiz.objects.create(title='Quiz 2', description='Desc 2', category=self.category2)

    # Test if the 'all-quiz.html' template is used and contains expected context
    def test_all_quiz_template(self):
        # Send GET request to 'all_quiz' view
        response = self.client.get(reverse('all_quiz'))

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'all-quiz.html')

        # Verify context contains 'quizzes' and 'categories'
        self.assertIn('quizzes', response.context)
        self.assertIn('categories', response.context)

        # Verify quiz titles and category names appear in the response content
        self.assertContains(response, 'Quiz 1')
        self.assertContains(response, 'Quiz 2')
        self.assertContains(response, 'Science')
        self.assertContains(response, 'English')

    # Test the case where no quizzes are available
    def test_no_quizzes(self):
        # Delete all quizzes to simulate an empty list
        Quiz.objects.all().delete()

        # Send GET request to 'all_quiz' view
        response = self.client.get(reverse('all_quiz'))

        # Verify that a 'no quiz available' message is displayed
        self.assertContains(response, 'There is no quiz available for this category or search.')
