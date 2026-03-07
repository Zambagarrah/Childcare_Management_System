from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
        limit_choices_to={'role': 'PARENT'},
        related_name='children_as_parent'
    )
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'CAREGIVER'},
        related_name='children_as_caregiver'
    )

    def clean(self):
        if self.age <= 0 or self.age > 18:
            raise ValidationError("Age must be between 1 and 18.")

    def __str__(self):
        return f"{self.name} (Age: {self.age})"

class CareNote(models.Model):
    child = models.ForeignKey('Child', on_delete=models.CASCADE, related_name='care_notes')
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CAREGIVER'}
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.child.name} by {self.caregiver.username}"

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class Activity(models.Model):
    child = models.ForeignKey('Child', on_delete=models.CASCADE, related_name='activities')
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CAREGIVER'}
    )
    activity_type = models.CharField(max_length=50)  # e.g. Meal, Nap, Lesson, Playtime
    description = models.TextField()
    scheduled_at = models.DateTimeField()

    def __str__(self):
        return f"{self.activity_type} for {self.child.name} at {self.scheduled_at}"
