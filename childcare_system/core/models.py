from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Custom user model for Childcare System
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('CAREGIVER', 'Caregiver'),
        ('PARENT', 'Parent'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='PARENT')

    def __str__(self):
        return f"{self.username} ({self.role})"

# Child model
class Child(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'PARENT'}
    )
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'CAREGIVER'}
    )

    def __str__(self):
        return f"{self.name} (Age: {self.age})"
