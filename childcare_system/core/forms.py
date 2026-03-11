from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Child

# Registration form with role selection
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'age', 'parent', 'caregiver']