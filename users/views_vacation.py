from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employees.models import Vacation
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def vacation_request(request):
    """Сотрудник подаёт заявку на отпуск"""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason', '').strip()

        if not start_date or not end_date:
            messages.error(request, 'Укажите даты начала и окончания отпуска')
        elif start_date > end_date:
            messages.error(request, 'Дата начала не может быть позже даты окончания')
        else:
            Vacation.objects.create(
                employee=request.user,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='pending'
            )
            messages.success(request, 'Заявка на отпуск отправлена!')
            return redirect('my_vacations')

    return render(request, 'users/vacation_request.html')


@login_required
def my_vacations(request):
    """Список заявок сотрудника"""
    vacations = Vacation.objects.filter(employee=request.user).order_by('-created_at')
    context = {'vacations': vacations}
    return render(request, 'users/my_vacations.html', context)


@login_required
def vacation_list(request):
    """Список всех заявок для директора/менеджера"""
    if request.user.role not in ['director', 'manager']:
        messages.error(request, 'Нет доступа')
        return redirect('dashboard')

    vacations = Vacation.objects.all().order_by('-created_at').select_related('employee')
    pending_count = vacations.filter(status='pending').count()

    context = {
        'vacations': vacations,
        'pending_count': pending_count,
    }
    return render(request, 'users/vacation_list.html', context)


@login_required
def vacation_approve(request, pk):
    """Одобрить заявку"""
    if request.user.role not in ['director', 'manager']:
        return redirect('dashboard')

    vacation = get_object_or_404(Vacation, pk=pk)
    vacation.status = 'approved'
    vacation.save()
    messages.success(request, f'Заявка одобрена!')
    return redirect('vacation_list')


@login_required
def vacation_reject(request, pk):
    """Отклонить заявку"""
    if request.user.role not in ['director', 'manager']:
        return redirect('dashboard')

    vacation = get_object_or_404(Vacation, pk=pk)
    vacation.status = 'rejected'
    vacation.save()
    messages.success(request, f'Заявка отклонена')
    return redirect('vacation_list')