#!/usr/bin/env python3

from django.contrib import admin
from .models import Category, Quiz, Question, Choice, QuizSubmission, UserRank

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Customize fields as needed
    search_fields = ('name',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text')
    list_filter = ('quiz',)
    search_fields = ('text',)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('question',)
    search_fields = ('text',)
    list_editable = ('is_correct',)

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'submitted_at')
    list_filter = ('quiz',)
    search_fields = ('user__username',)

@admin.register(UserRank)
class UserRankAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank')
    search_fields = ('user__username',)

# Optional: Register models directly if customization isn’t needed
admin.site.register(Category)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizSubmission)
admin.site.register(UserRank)
