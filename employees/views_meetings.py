from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meeting, MeetingRead
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


def meeting_create(request):
    if request.user.role not in ['director', 'manager']:
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        meeting_date = request.POST.get('date')
        meeting_time = request.POST.get('time')
        location = request.POST.get('location', '').strip()
        participant_ids = request.POST.getlist('participants')

        if not title or not meeting_date or not meeting_time:
            messages.error(request, 'Заполните тему, дату и время')
        else:
            meeting = Meeting.objects.create(
                title=title,
                description=description,
                date=meeting_date,
                time=meeting_time,
                location=location,
                organizer=request.user
            )
            if participant_ids:
                meeting.participants.set(participant_ids)
            messages.success(request, f'Встреча "{title}" создана!')
            return redirect('meeting_list')

    users = User.objects.exclude(id=request.user.id).order_by('role', 'username')
    return render(request, 'employees/meeting_create.html', {'users': users})


@login_required
def meeting_list(request):
    if request.user.role in ['director', 'manager']:
        from django.db.models import Q
        meetings = Meeting.objects.filter(
            Q(organizer=request.user) | Q(participants=request.user)
        ).distinct().prefetch_related('participants').order_by('date', 'time')
    else:
        meetings = Meeting.objects.filter(
            participants=request.user
        ).prefetch_related('participants').order_by('date', 'time')

    return render(request, 'employees/meeting_list.html', {
        'meetings': meetings,
        'today': date.today(),
        'now': __import__('datetime').datetime.now(),
    })


@login_required
def meeting_delete(request, pk):
    if request.user.role not in ['director', 'manager']:
        return redirect('dashboard')
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.delete()
    messages.success(request, 'Встреча удалена')
    return redirect('meeting_list')


@login_required
def meeting_read(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    MeetingRead.objects.get_or_create(user=request.user, meeting=meeting)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))