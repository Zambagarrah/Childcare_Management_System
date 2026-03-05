from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, ChildForm
from .models import Child, CareNote

# ---------------------------
# User Registration
# ---------------------------
def register(request):
    """Handles user registration with role selection."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# ---------------------------
# Role-Based Dashboard
# ---------------------------
@login_required
def dashboard(request):
    """Redirects user to role-specific dashboard."""
    if request.user.role == 'ADMIN':
        return render(request, 'dashboard_admin.html')
    elif request.user.role == 'CAREGIVER':
        return render(request, 'dashboard_caregiver.html')
    else:
        return render(request, 'dashboard_parent.html')


# ---------------------------
# Child CRUD Operations
# ---------------------------
@login_required
def child_list(request):
    """Displays children based on user role."""
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []
    return render(request, 'child_list.html', {'children': children})


@login_required
def child_create(request):
    """Allows Admins to create new child records."""
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
    """Allows Admins to update child records (including caregiver assignment)."""
    child = get_object_or_404(Child, pk=pk)
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can edit children.")
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
    """Allows Admins to delete child records."""
    child = get_object_or_404(Child, pk=pk)
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can delete children.")
    if request.method == 'POST':
        child.delete()
        return redirect('child_list')
    return render(request, 'child_confirm_delete.html', {'child': child})


# ---------------------------
# Care Notes (Business Logic)
# ---------------------------
@login_required
def care_notes(request, child_id):
    """Allows caregivers to add notes for assigned children.
        Parents and Admins can view notes but not add them."""
    child = get_object_or_404(Child, id=child_id)

    if request.user.role == 'CAREGIVER' and child.caregiver == request.user:
        if request.method == 'POST':
            note_text = request.POST.get('note')
            if note_text and note_text.strip():
                CareNote.objects.create(child=child, caregiver=request.user, note=note_text)
            else:
                return render(request, 'care_notes.html', {
                    'child': child,
                    'notes': child.care_notes.all(),
                    'error': "Note cannot be empty."
                })

    notes = child.care_notes.all()
    return render(request, 'care_notes.html', {'child': child, 'notes': notes})
