from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import User
from employees.models import Department, Employee, EmployeeSkill, Skill, Vacation
from tasks.models import Task
from teams.models import Team
from django.db.models import Q
from datetime import date, timedelta
from employees.models import Meeting, MeetingRead
from datetime import date


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'director':
                user.is_staff = True
            user.save()

            selected_skills = form.cleaned_data.get('skills', [])
            level = form.cleaned_data.get('skill_level', 'basic')
            for skill in selected_skills:
                EmployeeSkill.objects.create(employee=user, skill=skill, level=level)

            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')

            if user.role == 'director':
                return redirect('dashboard_director')
            elif user.role == 'manager':
                return redirect('dashboard_manager')
            else:
                return redirect('dashboard_employee')
        else:
            print("\n--- ОШИБКИ РЕГИСТРАЦИИ ---")
            for field, errors in form.errors.items():
                print(f"Поле '{field}': {errors}")
            print("--------------------------\n")
            messages.error(request, "Регистрация не удалась. Проверьте данные.")
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'director':
                return redirect('dashboard_director')
            elif user.role == 'manager':
                return redirect('dashboard_manager')
            elif user.role == 'employee':
                return redirect('dashboard_employee')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Неверный логин или пароль")

    return render(request, 'users/login.html')


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'director':
        return redirect('dashboard_director')
    elif user.role == 'manager':
        return redirect('dashboard_manager')
    else:
        return redirect('dashboard_employee')



@login_required
def dashboard_director(request):
    if request.user.role != 'director':
        messages.error(request, "У вас нет доступа к этому разделу.")
        return redirect('dashboard')

    from django.db.models import Count

    # Статистика
    total_users = User.objects.count()
    total_employees = User.objects.filter(role='employee').count()
    total_managers = User.objects.filter(role='manager').count()
    total_tasks = Task.objects.count()
    tasks_done = Task.objects.filter(status='done').count()

    # Топ сотрудников по выполненным задачам
    top_employees = User.objects.filter(role='employee').annotate(
        done_count=Count('assigned_tasks', filter=Q(assigned_tasks__status='done'))
    ).order_by('-done_count')[:5]

    # Топ команд по выполненным задачам
    from teams.models import Team
    top_teams = Team.objects.annotate(
        done_count=Count('task', filter=Q(task__status='done')),
        total_count=Count('task')
    ).order_by('-done_count')[:5]

    # Задачи по месяцам (последние 6 месяцев)
    from django.db.models.functions import TruncMonth
    from datetime import date, timedelta
    six_months_ago = date.today() - timedelta(days=180)
    tasks_by_month = Task.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Count('id'),
        done=Count('id', filter=Q(status='done'))
    ).order_by('month')

    months_labels = []
    months_total = []
    months_done = []
    for item in tasks_by_month:
        months_labels.append(item['month'].strftime('%b %Y'))
        months_total.append(item['total'])
        months_done.append(item['done'])

    # Последние зарегистрированные
    recent_users = User.objects.order_by('-date_joined')[:5]

    context = {
        'stats': {
            'total_users': total_users,
            'total_employees': total_employees,
            'total_managers': total_managers,
            'total_tasks': total_tasks,
            'tasks_done': tasks_done,
        },
        'top_employees': top_employees,
        'top_teams': top_teams,
        'months_labels': months_labels,
        'months_total': months_total,
        'months_done': months_done,
        'recent_users': recent_users,
    }

    upcoming_meetings = Meeting.objects.filter(
        organizer=request.user,
        date__gte=date.today()
    ).prefetch_related('participants').order_by('date', 'time')[:3]

    context['upcoming_meetings'] = upcoming_meetings

    # Уведомления о встречах куда пригласили директора
    read_ids = MeetingRead.objects.filter(user=request.user).values_list('meeting_id', flat=True)
    my_meetings = Meeting.objects.filter(
        participants=request.user,
        date__gte=date.today()
    ).exclude(id__in=read_ids).order_by('date', 'time')[:3]

    context['my_meetings'] = my_meetings
    return render(request, 'users/dashboard_director.html', context)


@login_required
def dashboard_manager(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    all_manager_tasks = Task.objects.filter(manager=request.user)
    total_all = all_manager_tasks.count()
    active_count = all_manager_tasks.exclude(status='done').count()
    done_count = total_all - active_count
    teams_count = Team.objects.filter(manager=request.user).count()

    active_employees = []
    employees_with_tasks = User.objects.filter(
        assigned_tasks__manager=request.user,
        assigned_tasks__status='inprogress'
    ).distinct()
    for emp in employees_with_tasks:
        emp.active_task_count = Task.objects.filter(
            employee=emp, manager=request.user, status='inprogress'
        ).count()
        active_employees.append(emp)

    deadline_tasks = Task.objects.filter(
        manager=request.user,
        due_date__range=[today, next_week]
    ).exclude(status='done').order_by('due_date')[:5]

    for task in deadline_tasks:
        task.is_today = task.due_date == today
        task.is_tomorrow = task.due_date == tomorrow

    pending_vacations = Vacation.objects.filter(status='pending').select_related('employee')[:3]

    # Исключаем прочитанные
    from employees.models import Meeting, MeetingRead

    read_ids = MeetingRead.objects.filter(user=request.user).values_list('meeting_id', flat=True)
    my_meetings = Meeting.objects.filter(
        participants=request.user,
        date__gte=today
    ).exclude(id__in=read_ids).order_by('date', 'time')[:3]

    context = {
        'stats': {
            'total_users': User.objects.count(),
            'total_employees': User.objects.filter(role='employee').count(),
            'total_tasks': active_count,
            'tasks_done': done_count,
            'my_teams_count': teams_count,
        },
        'active_employees': active_employees,
        'deadline_tasks': deadline_tasks,
        'pending_vacations': pending_vacations,
        'my_meetings': my_meetings,
    }
    return render(request, 'users/dashboard_manager.html', context)



@login_required
def dashboard_employee(request):
    if request.user.role != 'employee':
        messages.error(request, "У вас нет доступа к этому разделу.")
        return redirect('dashboard')

    today = date.today()
    tomorrow = today + timedelta(days=1)

    active_tasks = Task.objects.filter(
        employee=request.user
    ).exclude(status='done').order_by('due_date')[:5]

    for task in active_tasks:
        task.is_today = task.due_date == today if task.due_date else False
        task.is_tomorrow = task.due_date == tomorrow if task.due_date else False

    my_vacations = Vacation.objects.filter(
        employee=request.user
    ).order_by('-created_at')[:3]

    from employees.models import MeetingRead
    read_ids = MeetingRead.objects.filter(user=request.user).values_list('meeting_id', flat=True)
    my_meetings = Meeting.objects.filter(
        participants=request.user,
        date__gte=today
    ).exclude(id__in=read_ids).order_by('date', 'time')[:3]

    context = {
        'active_tasks': active_tasks,
        'my_vacations': my_vacations,
        'my_meetings': my_meetings,
    }
    return render(request, 'users/dashboard_employee.html', context)



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    context = {'users': users}
    return render(request, 'users/users_list.html', context)


@login_required
def staff_list(request):
    stats = {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_tasks': Task.objects.filter(manager=request.user).exclude(status='done').count(),
        'tasks_done': Task.objects.filter(manager=request.user, status='done').count(),
    }

    if request.user.role == 'employee':
        context = {
            'developers': User.objects.filter(role='employee').order_by('username'),
            'managers': None,
            'stats': stats,
            'is_employee_view': True,
        }
    else:
        context = {
            'managers': User.objects.filter(role='manager').order_by('username'),
            'developers': User.objects.filter(role='employee').order_by('username'),
            'stats': stats,
            'is_employee_view': False,
        }
    return render(request, 'users/staff_list.html', context)


@login_required
def global_search(request):
    query = request.GET.get('q', '')
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'query': query,
        'users': users,
        'stats': {}
    }
    return render(request, 'users/search_results.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            user.save()
            messages.success(request, 'Профиль обновлён!')

        elif action == 'add_skill':
            skill_id = request.POST.get('skill_id')
            level = request.POST.get('level', 'basic')
            if skill_id:
                skill = Skill.objects.filter(id=skill_id).first()
                if skill:
                    if not EmployeeSkill.objects.filter(employee=request.user, skill=skill).exists():
                        EmployeeSkill.objects.create(employee=request.user, skill=skill, level=level)
                        messages.success(request, f'Навык "{skill.name}" добавлен!')
                    else:
                        messages.warning(request, 'У вас уже есть этот навык')

        elif action == 'remove_skill':
            skill_id = request.POST.get('skill_id')
            if skill_id:
                EmployeeSkill.objects.filter(employee=request.user, skill_id=skill_id).delete()
                messages.success(request, 'Навык удалён')

        return redirect('profile')

    managed_teams = Team.objects.filter(manager=request.user)
    member_teams = Team.objects.filter(members=request.user)
    user_skills = EmployeeSkill.objects.filter(employee=request.user).select_related('skill')
    available_skills = Skill.objects.exclude(
        id__in=user_skills.values_list('skill_id', flat=True)
    )

    context = {
        'managed_teams': managed_teams,
        'member_teams': member_teams,
        'user_skills': user_skills,
        'available_skills': available_skills,
        'stats': {}
    }

    upcoming_meetings = Meeting.objects.filter(
        organizer=request.user,
        date__gte=date.today()
    ).order_by('date', 'time')[:3]

    context['upcoming_meetings'] = upcoming_meetings
    return render(request, 'users/profile.html', context)