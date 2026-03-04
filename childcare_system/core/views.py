from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ChildForm
from .models import Child

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

@login_required
def child_list(request):
    # Admin can see all children
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    # Parent can only see their own children
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    # Caregiver can only see children assigned to them
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []

    return render(request, 'child_list.html', {'children': children})

@login_required
def child_create(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can add children.")
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('child_list')
    else:
        form = ChildForm()
    return render(request, 'child_form.html', {'form': form})

@login_required
def child_update(request, pk):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can edit children.")
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            return redirect('child_list')
    else:
        form = ChildForm(instance=child)
    return render(request, 'child_form.html', {'form': form})

@login_required
def child_delete(request, pk):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can delete children.")
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        child.delete()
        return redirect('child_list')
    return render(request, 'child_confirm_delete.html', {'child': child})
