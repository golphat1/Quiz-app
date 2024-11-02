from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Profile model to extend the User model with additional fields
class Profile(models.Model):
    """
    Represents additional information for a user profile.

    Attributes:
        user (OneToOneField): Links Profile to Django's User model.
        bio (TextField): Optional bio field for the user.
        profile_picture (ImageField): Optional profile picture for the user.
        created_at (DateTimeField): Timestamp for when the profile was created.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the profile instance, typically
        used for displaying the profile owner's username.

        Returns:
            str: Username associated with this profile.
        """
        return f"{self.user.username}'s Profile"


# Message model for creating and managing user messages
class Message(models.Model):
    """
    Model representing messages between users.

    Attributes:
        user (ForeignKey): User who created the message.
        subject (CharField): The subject/title of the message.
        message (TextField): The content of the message.
        is_read (BooleanField): Status indicating if the message has been read.
        created_at (DateTimeField): Timestamp for when the message was created.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the message instance.

        Returns:
            str: Username and subject of the message.
        """
        return f"{self.user.username}, {self.subject}"


# Blog model for creating and managing blog posts
class Blog(models.Model):
    """
    Model representing a blog post.

    Attributes:
        title (CharField): Title of the blog post.
        content (RichTextField): Content of the blog post with rich text formatting.
        author (ForeignKey): User who authored the blog post.
        status (CharField): Visibility status of the blog post, either public or private.
        created_at (DateTimeField): Timestamp for when the blog post was created.
        updated_at (DateTimeField): Timestamp for when the blog post was last updated.
    """
    title = models.CharField(max_length=255)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    status = models.CharField(max_length=7, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the blog instance.

        Returns:
            str: Title of the blog post.
        """
        return self.title
