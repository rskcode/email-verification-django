from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission, Group

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Specify a different related name for user_permissions
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    
    # Specify a different related name for groups
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    def __str__(self):
        return self.username

class Group(models.Model):
    # Specify a different related name for groups
    user_set = models.ManyToManyField(
        CustomUser,
        related_name='custom_group_set',
        related_query_name='custom_group'
    )

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, verbose_name='User Object')
    bio = models.TextField(blank=True, null=True)
    isPremium = models.BooleanField(default=False)