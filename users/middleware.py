from django.shortcuts import redirect
from django.contrib import messages


class RoleBasedAdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Если пользователь пытается зайти в админку
        if request.path.startswith('/admin/'):
            # Если пользователь не авторизован - пусть работает стандартная логика Django (редирект на логин)
            if not request.user.is_authenticated:
                return self.get_response(request)

            # Если авторизован, проверяем роль
            # Только директор может в админку
            if hasattr(request.user, 'role') and request.user.role != 'director':
                messages.error(request, "Доступ запрещён: Только Директор может использовать Админ-панель.")
                # Кидаем на дашборд директора или его личный кабинет
                return redirect('dashboard_director')

        response = self.get_response(request)
        return response