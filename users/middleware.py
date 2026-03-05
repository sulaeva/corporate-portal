from django.shortcuts import redirect
from django.contrib import messages


class RoleBasedAdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                if not request.user.is_superuser and request.user.role != 'director':
                    from django.http import HttpResponseForbidden
                    return HttpResponseForbidden('Доступ запрещён. Только для директоров.')
        return self.get_response(request)