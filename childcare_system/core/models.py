from django.contrib.auth.models import AbstractUser
from django.db import models

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
