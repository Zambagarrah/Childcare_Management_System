from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import csv
from reportlab.pdfgen import canvas

from .models import Child, CareNote, Activity, Message, User
from .forms import ChildForm
from django.contrib.auth.forms import UserCreationForm


# ---------------------------
# AUTH / REGISTER
# ---------------------------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# ---------------------------
# Home Page
# ---------------------------
def home(request):
    return render(request, 'home.html')

# ---------------------------
# CHILD CRUD
# ---------------------------
@login_required
def child_list(request):
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []
    return render(request, 'child_list.html', {'children': children})

#
# @login_required
# def child_create(request):
#     if request.user.role != 'ADMIN':
#         return HttpResponseForbidden("Only Admins can create children.")
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         age = int(request.POST.get('age'))
#         parent_id = request.POST.get('parent')
#         caregiver_id = request.POST.get('caregiver')
#
#         if age < 1 or age > 18:
#             messages.error(request, "Age must be between 1 and 18.")
#         else:
#             parent = get_object_or_404(User, id=parent_id)
#             caregiver = get_object_or_404(User, id=caregiver_id) if caregiver_id else None
#             Child.objects.create(name=name, age=age, parent=parent, caregiver=caregiver)
#             messages.success(request, "Child created successfully!")
#             return redirect('child_list')
#     return render(request, 'child_form.html')
#
#
# @login_required
# def child_update(request, child_id):
#     if request.user.role != 'ADMIN':
#         return HttpResponseForbidden("Only Admins can update children.")
#     child = get_object_or_404(Child, id=child_id)
#     if request.method == 'POST':
#         child.name = request.POST.get('name')
#         child.age = int(request.POST.get('age'))
#         caregiver_id = request.POST.get('caregiver')
#         child.caregiver = get_object_or_404(User, id=caregiver_id) if caregiver_id else None
#         child.save()
#         messages.success(request, "Child updated successfully!")
#         return redirect('child_list')
#     return render(request, 'child_form.html', {'child': child})

@login_required
def child_create(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can create children.")
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Child created successfully!")
            return redirect('child_list')
    else:
        form = ChildForm()
    return render(request, 'child_form.html', {'form': form})

@login_required
def child_update(request, child_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can update children.")
    child = get_object_or_404(Child, id=child_id)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, "Child updated successfully!")
            return redirect('child_list')
    else:
        form = ChildForm(instance=child)
    return render(request, 'child_form.html', {'form': form})



@login_required
def child_delete(request, child_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Only Admins can delete children.")
    child = get_object_or_404(Child, id=child_id)
    child.delete()
    messages.success(request, "Child deleted successfully!")
    return redirect('child_list')


# ---------------------------
# CARE NOTES
# ---------------------------
@login_required
def care_notes(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    notes = child.care_notes.all().order_by('-created_at')

    if request.method == 'POST':
        if request.user.role == 'CAREGIVER' and child.caregiver == request.user:
            content = request.POST.get('note')
            if content.strip():
                CareNote.objects.create(child=child, caregiver=request.user, note=content)
                messages.success(request, "Care note added successfully!")
                return redirect('care_notes', child_id=child.id)
            else:
                messages.error(request, "Note cannot be empty.")
        else:
            return HttpResponseForbidden("Only assigned caregiver can add notes.")

    return render(request, 'care_notes.html', {'child': child, 'notes': notes})

@login_required
def care_notes_report(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    # Parents can only view their own child’s notes
    if request.user.role == 'PARENT' and child.parent != request.user:
        return HttpResponseForbidden("You cannot view notes for another parent's child.")

    notes = child.care_notes.all().order_by('-created_at')
    return render(request, 'care_notes_report.html', {
        'child': child,
        'notes': notes
    })


# ---------------------------
# REPORTING
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


@login_required
def export_summary_csv(request):
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summary.csv"'
    writer = csv.writer(response)
    writer.writerow(['Child', 'Notes Count', 'Activities Count'])

    for child in children:
        writer.writerow([child.name, child.care_notes.count(), child.activities.count()])

    return response


@login_required
def export_summary_pdf(request):
    if request.user.role == 'ADMIN':
        children = Child.objects.all()
    elif request.user.role == 'PARENT':
        children = request.user.children_as_parent.all()
    elif request.user.role == 'CAREGIVER':
        children = request.user.children_as_caregiver.all()
    else:
        children = []

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="summary.pdf"'
    p = canvas.Canvas(response)

    p.drawString(100, 800, "Childcare Reporting Summary")
    y = 760
    for child in children:
        line = f"{child.name} — Notes: {child.care_notes.count()} | Activities: {child.activities.count()}"
        p.drawString(100, y, line)
        y -= 20

    p.showPage()
    p.save()
    return response


# ---------------------------
# MESSAGING
# ---------------------------
@login_required
def inbox(request):
    messages_qs = Message.objects.filter(recipient=request.user).order_by('-created_at')
    users = User.objects.exclude(id=request.user.id)  # exclude self
    return render(request, 'inbox.html', {'messages': messages_qs, 'users': users})

@login_required
def send_message(request, recipient_id=None):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id') or recipient_id
        recipient = get_object_or_404(User, id=recipient_id)
        content = request.POST.get('content')
        if content.strip():
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            messages.success(request, "Message sent successfully!")
            return redirect('inbox')
        else:
            messages.error(request, "Message cannot be empty.")
    else:
        recipient = get_object_or_404(User, id=recipient_id) if recipient_id else None
    return render(request, 'send_message.html', {'recipient': recipient})


# ---------------------------
# ACTIVITIES
# ---------------------------
@login_required
def activity_list(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    activities = child.activities.all().order_by('scheduled_at')
    return render(request, 'activity_list.html', {'child': child, 'activities': activities})


@login_required
def add_activity(request, child_id):
    child = get_object_or_404(Child, id=child_id)

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
            messages.success(request, "Activity scheduled successfully!")
            return redirect('activity_list', child_id=child.id)
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'add_activity.html', {'child': child})

@login_required
def dashboard(request):
    if request.user.role == 'ADMIN':
        # Admin sees system-wide stats
        total_children = Child.objects.count()
        total_parents = User.objects.filter(role='PARENT').count()
        total_caregivers = User.objects.filter(role='CAREGIVER').count()
        total_notes = CareNote.objects.count()
        total_activities = Activity.objects.count()

        context = {
            'role': 'ADMIN',
            'total_children': total_children,
            'total_parents': total_parents,
            'total_caregivers': total_caregivers,
            'total_notes': total_notes,
            'total_activities': total_activities,
        }

    elif request.user.role == 'PARENT':
        # Parent sees their children stats
        children = request.user.children_as_parent.all()
        notes_count = sum(child.care_notes.count() for child in children)
        activities_count = sum(child.activities.count() for child in children)

        context = {
            'role': 'PARENT',
            'children': children,
            'notes_count': notes_count,
            'activities_count': activities_count,
        }

    elif request.user.role == 'CAREGIVER':
        # Caregiver sees assigned children stats
        children = request.user.children_as_caregiver.all()
        notes_count = sum(child.care_notes.count() for child in children)
        activities_count = sum(child.activities.count() for child in children)

        context = {
            'role': 'CAREGIVER',
            'children': children,
            'notes_count': notes_count,
            'activities_count': activities_count,
        }

    else:
        context = {'role': 'UNKNOWN'}

    return render(request, 'dashboard.html', context)
