from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from users.decorators import role_required
from django.contrib.auth import get_user_model
from teams.models import Team

User = get_user_model()


@login_required
def task_list(request):
    # ✅ Сотрудник видит только свои задачи
    if request.user.role == 'employee':
        tasks = Task.objects.filter(employee=request.user).exclude(status='done').order_by('-created_at')
        context = {
            'tasks': tasks,
            'is_employee_view': True,  # ← добавлено
            'stats': {
                'total_tasks': tasks.count(),
                'tasks_done': Task.objects.filter(employee=request.user, status='done').count(),
                'total_users': User.objects.count(),
                'total_employees': User.objects.filter(role='employee').count(),
            }
        }
        return render(request, 'tasks/task_list.html', context)

    # Для директора и менеджера — старая логика
    tasks = Task.objects.exclude(status='done').order_by('-created_at')

    selected_employee = None
    selected_manager = None
    active_tasks_count = 0
    done_tasks_count = 0

    employee_id = request.GET.get('employee')
    if employee_id:
        try:
            tasks = tasks.filter(employee_id=employee_id)
            selected_employee = User.objects.get(id=employee_id)
            active_tasks_count = tasks.count()
        except (ValueError, User.DoesNotExist):
            pass

    manager_id = request.GET.get('manager')
    if manager_id:
        try:
            tasks = tasks.filter(manager_id=manager_id)
            selected_manager = User.objects.get(id=manager_id)
            active_tasks_count = tasks.count()
        except (ValueError, User.DoesNotExist):
            pass

    if not employee_id and not manager_id:
        active_tasks_count = tasks.count()

    if manager_id:
        done_tasks_count = Task.objects.filter(manager_id=manager_id, status='done').count()
    elif employee_id:
        done_tasks_count = Task.objects.filter(employee_id=employee_id, status='done').count()
    else:
        done_tasks_count = Task.objects.filter(status='done').count()

    context = {
        'tasks': tasks,
        'selected_employee': selected_employee,
        'selected_manager': selected_manager,
        'is_employee_view': False,
        'stats': {
            'total_tasks': active_tasks_count,
            'tasks_done': done_tasks_count,
            'total_users': User.objects.count(),
            'total_employees': User.objects.filter(role='employee').count(),
        }
    }
    return render(request, 'tasks/task_list.html', context)

@role_required(['director', 'manager'])
def task_create(request, employee_id=None, team_id=None):
    initial_data = {}

    # Если передан ID сотрудника, подставляем его
    if employee_id:
        try:
            selected_employee = User.objects.get(id=employee_id)
            initial_data['employee'] = selected_employee
        except User.DoesNotExist:
            pass

    # Если передан ID команды, подставляем её
    if team_id:
        try:
            selected_team = Team.objects.get(id=team_id)
            initial_data['team'] = selected_team
        except Team.DoesNotExist:
            pass

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.manager = request.user

            # Если вдруг поле оказалось пустым (редкий случай), пробуем взять из URL снова
            if not task.employee and employee_id:
                try:
                    task.employee = User.objects.get(id=employee_id)
                except:
                    pass

            if not task.team and team_id:
                try:
                    task.team = Team.objects.get(id=team_id)
                except:
                    pass

            task.save()
            messages.success(request, 'Задача успешно создана!')

            # Возвращаемся к списку задач этого сотрудника
            if employee_id and team_id:
                return redirect('employee_tasks', employee_id=employee_id, team_id=team_id)
            return redirect('task_list')
    else:
        # GET запрос: создаем форму с уже выбранными полями
        form = TaskForm(initial=initial_data)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'selected_employee_id': employee_id,  # Передаем ID для скрытого поля (на всякий случай)
        'selected_team_id': team_id
    })



@role_required(['director', 'manager'])
def task_edit(request, pk):
    """Редактирование задачи"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача обновлена!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'edit', 'task': task})


@role_required(['director', 'manager'])
def task_delete(request, pk):
    """Удаление задачи"""
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'Задача удалена!')
    return redirect('task_list')


@login_required
def task_detail(request, pk):
    """Детали задачи"""
    task = get_object_or_404(Task, pk=pk)

    # Проверка доступа
    if not (request.user == task.employee or
            request.user == task.manager or
            getattr(request.user, 'role', '') == 'director'):
        messages.error(request, 'У вас нет доступа к этой задаче')
        return redirect('dashboard')

    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_change_status(request, pk, new_status):
    task = get_object_or_404(Task, pk=pk)

    if request.user != task.employee and getattr(request.user, 'role', '') != 'director':
        messages.error(request, 'Только исполнитель или директор может менять статус')
        return redirect('task_detail', pk=pk)

    status_order = ['todo', 'inprogress', 'done']

    if new_status not in status_order:
        messages.error(request, 'Неверный статус')
        return redirect('task_detail', pk=pk)

    current_index = status_order.index(task.status)
    new_index = status_order.index(new_status)

    if request.user != task.employee and getattr(request.user, 'role', '') == 'director':
        pass
    elif new_index <= current_index:
        messages.error(request, 'Нельзя вернуть задачу в предыдущий статус')
        return redirect('task_detail', pk=pk)

    task.status = new_status
    task.save()

    status_names = {'todo': 'Новая', 'inprogress': 'В работе', 'done': 'Выполнено'}
    messages.success(request, f'Статус изменён на {status_names[new_status]}')

    # ✅ Редирект по роли
    if request.user.role == 'employee':
        return redirect('task_list')
    elif request.user.role == 'manager':
        return redirect('task_list')
    else:
        return redirect('task_list')



@login_required
def task_done_list(request):
    if request.user.role == 'employee':
        tasks = Task.objects.filter(employee=request.user, status='done').order_by('-updated_at')
    elif request.user.role == 'manager':
        tasks = Task.objects.filter(manager=request.user, status='done').order_by('-updated_at')
    else:
        tasks = Task.objects.filter(status='done').order_by('-updated_at')
    context = {'tasks': tasks}
    return render(request, 'tasks/task_done_list.html', context)


@role_required(['director', 'manager'])
def employee_tasks(request, employee_id, team_id):
    employee = get_object_or_404(User, id=employee_id)
    team = get_object_or_404(Team, id=team_id)

    # ✅ Показываем ВСЕ задачи включая выполненные
    tasks = Task.objects.filter(employee=employee, team=team).order_by('-created_at')

    context = {
        'tasks': tasks,
        'employee': employee,
        'team': team,
        'page_title': f'Задачи: {employee.get_full_name() or employee.username} ({team.name})'
    }
    return render(request, 'tasks/employee_tasks_list.html', context)