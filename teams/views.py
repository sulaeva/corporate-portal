from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team
from .forms import TeamForm
from tasks.models import Task

# !!! ВАЖНО: Получаем кастомную модель пользователя правильно !!!
from django.contrib.auth import get_user_model

User = get_user_model()



@login_required
def my_teams_list(request):
    teams = Team.objects.filter(members=request.user)  # Или manager=request.user

    # !!! Расчет статистики !!!
    stats = {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_tasks': Task.objects.filter(manager=request.user).exclude(status='done').count(),
        'tasks_done': Task.objects.filter(manager=request.user, status='done').count(),
    }

    context = {
        'teams': teams,
        'stats': stats  # !!! Не забудь передать !!!
    }
    return render(request, 'teams/my_teams_list.html', context)


@login_required
def team_create(request):
    """Создание новой команды"""
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.manager = request.user
            team.save()
            form.save_m2m()
            # Добавляем создателя в участники
            team.members.add(request.user)
            return redirect('my_teams_list')
    else:
        form = TeamForm()
    return render(request, 'teams/team_form.html', {'form': form})


@login_required
def team_delete(request, pk):
    """
    Страница управления командой: просмотр, добавление и удаление участников.
    Доступна только менеджеру этой команды.
    """
    team = get_object_or_404(Team, pk=pk)

    # Проверка прав: если пользователь не менеджер этой команды, запрещаем доступ
    if team.manager != request.user:
        messages.error(request, "У вас нет прав для управления этой командой.")
        return redirect('my_teams_list')

    members = team.members.all()

    # --- ЛОГИКА ДОБАВЛЕНИЯ УЧАСТНИКА ---
    if request.method == 'POST' and 'add_member_id' in request.POST:
        user_id = request.POST.get('add_member_id')
        if user_id:
            user_to_add = get_object_or_404(User, id=user_id)
            if user_to_add not in members:
                team.members.add(user_to_add)
                messages.success(request, f"Пользователь {user_to_add.username} добавлен в команду.")
            else:
                messages.warning(request, "Этот пользователь уже в команде.")
        return redirect('team_detail', pk=team.pk)

    # --- ЛОГИКА УДАЛЕНИЯ УЧАСТНИКА ---
    if request.method == 'POST' and 'remove_member_id' in request.POST:
        user_id = request.POST.get('remove_member_id')
        if user_id:
            user_to_remove = get_object_or_404(User, id=user_id)
            if user_to_remove in members:
                if user_to_remove == team.manager:
                    messages.error(request, "Нельзя удалить лидера команды таким способом.")
                else:
                    team.members.remove(user_to_remove)
                    messages.success(request, f"Пользователь {user_to_remove.username} удален из команды.")
        return redirect('team_detail', pk=team.pk)

    available_employees = User.objects.filter(role='employee').exclude(
        id__in=members.values_list('id', flat=True)
    ).exclude(
        id=team.manager.id
    )

    context = {
        'team': team,
        'members': members,
        'available_employees': available_employees,
        'stats': {}
    }
    return render(request, 'teams/team_detail.html', context)


