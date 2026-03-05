from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import User
from employees.models import Department, Employee
from tasks.models import Task
from teams.models import Team
from django.db.models import Q # Важно для сложного поиска
from employees.models import EmployeeSkill



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'director':
                user.is_staff = True
            user.save()

            # ✅ Сохраняем навыки
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


# --- Вход в систему (Login) ---
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ АВТОМАТИЧЕСКИЙ РЕДИРЕКТ ПО РОЛИ
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


# --- Главный роутер (Dashboard) ---
@login_required
def dashboard(request):
    """
    Перенаправляет пользователя на страницу его роли.
    """
    user = request.user

    if user.role == 'director':
        return redirect('dashboard_director')
    elif user.role == 'manager':
        return redirect('dashboard_manager')
    else:
        return redirect('dashboard_employee')


# --- Dashboard Директора ---
@login_required
def dashboard_director(request):
    # ✅ СТРОГАЯ ПРОВЕРКА: Только директор
    if request.user.role != 'director':
        messages.error(request, "У вас нет доступа к этому разделу. Только для Директора.")
        return redirect('dashboard')

    stats = {
        'total_users': User.objects.count(),  # Исправлено: считаем всех пользователей
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
    # 1. ВСЕ задачи менеджера
    all_manager_tasks = Task.objects.filter(manager=request.user)
    total_all = all_manager_tasks.count()

    # 2. Активные (не выполненные)
    # Мы используем exclude(status='done'), так как это стандарт
    active_count = all_manager_tasks.exclude(status='done').count()

    # 3. Выполненные = ВСЕ - АКТИВНЫЕ
    # Это железобетонный способ, который сработает даже если статус называется криво
    done_count = total_all - active_count

    teams_count = Team.objects.filter(manager=request.user).count()

    stats = {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_tasks': active_count,
        'tasks_done': done_count, # Теперь тут точно будет 2
        'my_teams_count': teams_count,
    }

    context = {'stats': stats}
    return render(request, 'users/dashboard_manager.html', context)


@login_required
def dashboard_employee(request):
    if request.user.role != 'employee':
        messages.error(request, "У вас нет доступа к этому разделу.")
        return redirect('dashboard')

    # ✅ Только активные задачи (не выполненные)
    my_tasks = Task.objects.filter(employee=request.user).exclude(status='done')

    context = {
        'my_tasks': my_tasks,
    }
    return render(request, 'users/dashboard_employee.html', context)


# --- Выход ---
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def users_list(request):
    # Показываем ВСЕХ пользователей
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

    # Для сотрудника показываем только коллег-сотрудников
    if request.user.role == 'employee':
        context = {
            'developers': User.objects.filter(role='employee').order_by('username'),
            'managers': None,  # ← не передаём менеджеров
            'stats': stats,
            'is_employee_view': True,  # ← флаг для шаблона
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
        # Ищем по логину, имени, фамилии или email
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'query': query,
        'users': users,
        'stats': {}  # Если в base.html требуется контекст stats, передай пустой или реальный
    }
    return render(request, 'users/search_results.html', context)


@login_required
def profile(request):
    managed_teams = Team.objects.filter(manager=request.user)
    member_teams = Team.objects.filter(members=request.user)

    context = {
        'managed_teams': managed_teams,
        'member_teams': member_teams,
        'stats': {}  # Пустая статистика, чтобы не ломался base.html
    }
    return render(request, 'users/profile.html', context)