from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import User
from employees.models import Department, Employee, EmployeeSkill, Skill
from tasks.models import Task
from teams.models import Team
from django.db.models import Q


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

    stats = {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_managers': User.objects.filter(role='manager').count(),
        'total_tasks': Task.objects.count(),
        'tasks_done': Task.objects.filter(status='done').count(),
    }
    tasks = Task.objects.all()[:5]
    context = {'stats': stats, 'tasks': tasks}
    return render(request, 'users/dashboard_director.html', context)


@login_required
def dashboard_manager(request):
    all_manager_tasks = Task.objects.filter(manager=request.user)
    total_all = all_manager_tasks.count()
    active_count = all_manager_tasks.exclude(status='done').count()
    done_count = total_all - active_count
    teams_count = Team.objects.filter(manager=request.user).count()

    stats = {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_tasks': active_count,
        'tasks_done': done_count,
        'my_teams_count': teams_count,
    }
    context = {'stats': stats}
    return render(request, 'users/dashboard_manager.html', context)


@login_required
def dashboard_employee(request):
    if request.user.role != 'employee':
        messages.error(request, "У вас нет доступа к этому разделу.")
        return redirect('dashboard')

    context = {}
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
    return render(request, 'users/profile.html', context)