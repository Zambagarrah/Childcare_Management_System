from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, ChildForm
from .models import Child, CareNote, Message, Activity

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

# ---------------------------
# Reporting
# ---------------------------
@login_required
def child_report(request):
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []
    return render(request, 'child_report.html', {'children': children})

@login_required
def care_notes_report(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    # Parents can only view their own child’s notes
    if request.user.role == 'PARENT' and child.parent != request.user:
        return HttpResponseForbidden("You cannot view notes for another parent's child.")

    notes = child.care_notes.all().order_by('-created_at')
    return render(request, 'care_notes_report.html', {'child': child, 'notes': notes})

@login_required
def reporting_summary(request):
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []

    total_children = children.count()
    total_notes = sum(child.care_notes.count() for child in children)
    total_activities = sum(child.activities.count() for child in children)

    avg_notes_per_child = total_notes / total_children if total_children > 0 else 0
    avg_activities_per_child = total_activities / total_children if total_children > 0 else 0

    return render(request, 'reporting_summary.html', {
        'children': children,
        'total_children': total_children,
        'total_notes': total_notes,
        'total_activities': total_activities,
        'avg_notes_per_child': avg_notes_per_child,
        'avg_activities_per_child': avg_activities_per_child,
    })


# ---------------------------
# Messaging
# ---------------------------
@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'inbox.html', {'messages': messages})

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            return redirect('inbox')
    return render(request, 'send_message.html', {'recipient': recipient})

# ---------------------------
# Activity Logs
# ---------------------------
@login_required
def activity_list(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    activities = child.activities.all().order_by('scheduled_at')
    return render(request, 'activity_list.html', {'child': child, 'activities': activities})

@login_required
def add_activity(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    # Only assigned caregiver can add activities
    if request.user.role != 'CAREGIVER' or child.caregiver != request.user:
        return HttpResponseForbidden("Only the assigned caregiver can add activities.")

    if request.method == 'POST':
        activity_type = request.POST.get('activity_type')
        description = request.POST.get('description')
        scheduled_at = request.POST.get('scheduled_at')

        if activity_type.strip() and description.strip() and scheduled_at.strip():
            Activity.objects.create(
                child=child,
                caregiver=request.user,
                activity_type=activity_type,
                description=description,
                scheduled_at=scheduled_at
            )
            return redirect('activity_list', child_id=child.id)

    return render(request, 'add_activity.html', {'child': child})
