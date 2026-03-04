from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Декоратор для проверки роли пользователя.
    allowed_roles: список или строка с разрешёнными ролями (например, ['director'])
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Нормализуем входные данные (чтобы работало и со строкой, и со списком)
            if isinstance(allowed_roles, str):
                allowed = [allowed_roles]
            else:
                allowed = allowed_roles

            if request.user.role not in allowed:
                # Если роль не подходит
                messages.error(request, "У вас нет доступа к этому разделу.")

                # Перенаправляем на правильную страницу в зависимости от роли пользователя
                if request.user.role == 'director':
                    return redirect('dashboard_director')  # Или 'admin'
                elif request.user.role == 'manager':
                    return redirect('dashboard_manager')
                else:
                    return redirect('dashboard_employee')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator