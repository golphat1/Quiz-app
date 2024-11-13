#!/usr/bin/env python3

from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('settings', views.editProfile, name='edit_profile'),
    path('delete', views.deleteProfile, name='delete_profile'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    #path('user/profile/<username>/', views.profile, name='profile'),
    path('user/profile/<str:username>/', views.profile, name='profile'),

]