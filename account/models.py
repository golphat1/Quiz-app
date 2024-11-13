#!/usr/bin/env python3

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    A model that extends the built-in User model to store additional information about the user.
    """

    # Establish a one-to-one relationship with Django's built-in User model.
    # 'on_delete=models.CASCADE' ensures that if the User is deleted, the Profile is also deleted.
    # 'null=True' allows for nullable relationships, and 'verbose_name' gives a human-readable name in the admin interface.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, verbose_name='User Object')

    # A biography field to store text data about the user; it allows blank and null values.
    bio = models.TextField(blank=True, null=True)

    # An image field for the user's profile picture.
    # Images will be uploaded to the 'profile_images' directory, with a default image of 'user.png'.
    # 'blank=True' allows the field to be optional in forms, and 'null=True' allows it to store null values in the database.
    profile_img = models.ImageField(upload_to='profile_images', default='user.png', blank=True, null=True, verbose_name='Profile Pic')

    # A field to store the user's location with a maximum character limit of 100.
    # 'blank=True' and 'null=True' make this field optional.
    location = models.CharField(max_length=100, blank=True, null=True)

    # Choices for the user's gender.
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    # A field to store the user's gender with options from the 'GENDER' choices.
    # It has a maximum length of 6 characters to accommodate the longest choice.
    gender = models.CharField(max_length=6, choices=GENDER, blank=True, null=True)

    def __str__(self):
        """
        Returns the username associated with this profile for easy identification in the admin panel.
        """
        return self.user.username

    @property
    def full_name(self):
        """
        Returns the full name of the user by concatenating the first and last names.
        This property is useful when displaying the full name in templates or views.
        """
        return f"{self.user.first_name} {self.user.last_name}"
