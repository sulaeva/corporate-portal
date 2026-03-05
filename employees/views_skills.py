from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Skill, EmployeeSkill
from django.contrib.auth import get_user_model

User = get_user_model()


def get_stats(user):
    from tasks.models import Task
    return {
        'total_users': User.objects.count(),
        'total_employees': User.objects.filter(role='employee').count(),
        'total_tasks': Task.objects.filter(manager=user).exclude(status='done').count(),
        'tasks_done': Task.objects.filter(manager=user, status='done').count(),
    }


@login_required
def skills_list(request):
    if request.user.role not in ['director', 'manager']:
        messages.error(request, 'Нет доступа')
        return redirect('dashboard')

    skills = Skill.objects.all().order_by('category', 'name')
    context = {
        'skills': skills,
        'stats': get_stats(request.user),
    }
    return render(request, 'employees/skills_list.html', context)


@login_required
def skill_add(request):
    if request.user.role not in ['director', 'manager']:
        messages.error(request, 'Нет доступа')
        return redirect('dashboard')

    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('framework', 'Framework'),
        ('database', 'Database'),
        ('soft_skills', 'Soft Skills'),
        ('language', 'Language'),
        ('tools', 'Tools'),
    ]

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '')
        description = request.POST.get('description', '').strip()

        if not name or not category:
            messages.error(request, 'Заполните название и категорию')
        elif Skill.objects.filter(name=name).exists():
            messages.error(request, 'Такой навык уже существует')
        else:
            Skill.objects.create(name=name, category=category, description=description)
            messages.success(request, f'Навык "{name}" добавлен!')
            return redirect('skills_list')

    context = {
        'categories': CATEGORY_CHOICES,
        'stats': get_stats(request.user),
    }
    return render(request, 'employees/skill_add.html', context)


@login_required
def skill_detail(request, pk):
    if request.user.role not in ['director', 'manager']:
        messages.error(request, 'Нет доступа')
        return redirect('dashboard')

    skill = get_object_or_404(Skill, pk=pk)
    # Сотрудники с этим навыком
    employee_skills = EmployeeSkill.objects.filter(skill=skill).select_related('employee')
    # Сотрудники без этого навыка
    employees_without = User.objects.filter(role='employee').exclude(
        id__in=employee_skills.values_list('employee_id', flat=True)
    )

    context = {
        'skill': skill,
        'employee_skills': employee_skills,
        'employees_without': employees_without,
        'stats': get_stats(request.user),
    }
    return render(request, 'employees/skill_detail.html', context)


@login_required
def skill_delete(request, pk):
    if request.user.role != 'director':
        messages.error(request, 'Только директор может удалять навыки')
        return redirect('skills_list')

    skill = get_object_or_404(Skill, pk=pk)
    skill.delete()
    messages.success(request, f'Навык удалён')
    return redirect('skills_list')


@login_required
def skill_assign(request, pk):
    """Назначить навык сотруднику"""
    if request.user.role not in ['director', 'manager']:
        return redirect('dashboard')

    skill = get_object_or_404(Skill, pk=pk)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        level = request.POST.get('level', 'basic')
        if employee_id:
            employee = get_object_or_404(User, id=employee_id)
            if not EmployeeSkill.objects.filter(employee=employee, skill=skill).exists():
                EmployeeSkill.objects.create(employee=employee, skill=skill, level=level)
                messages.success(request, f'Навык назначен сотруднику {employee.username}')
            else:
                messages.warning(request, 'У сотрудника уже есть этот навык')

    return redirect('skill_detail', pk=pk)