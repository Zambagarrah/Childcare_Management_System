from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm


# Registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('dashboard')  # redirect to dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == 'ADMIN':
        return render(request, 'dashboard_admin.html')
    elif request.user.role == 'CAREGIVER':
        return render(request, 'dashboard_caregiver.html')
    else:
        return render(request, 'dashboard_parent.html')

