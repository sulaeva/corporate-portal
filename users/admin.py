from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# ================= БАЗОВЫЕ НАСТРОЙКИ =================
class BaseUserConfig(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')  # Фильтр по статусу

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'phone', 'position', 'role')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


# ================= PROXY МОДЕЛИ (ВИРТУАЛЬНЫЕ КЛАССЫ) =================
# Они не создают новых таблиц в БД, а просто говорят Админке:
# "Считай нас отдельными сущностями для отображения"

class ManagerProxy(User):
    """Прокси-модель для Менеджеров"""

    class Meta:
        proxy = True
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"


class EmployeeProxy(User):
    """Прокси-модель для Сотрудников"""

    class Meta:
        proxy = True
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class DirectorProxy(User):
    """Прокси-модель для Директоров"""

    class Meta:
        proxy = True
        verbose_name = "Директор"
        verbose_name_plural = "Директора"


# ================= АДМИНКИ ДЛЯ ПРОКСИ =================

@admin.register(ManagerProxy)
class ManagerAdmin(BaseUserConfig):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='manager')  # Показываем только менеджеров

    def has_add_permission(self, request):
        # Запрещаем создание прямо здесь, чтобы не запутаться,
        # или можно разрешить, но тогда нужно форсировать роль в форме.
        # Для простоты оставим True, но в форме создания будет выбор роли.
        return True


@admin.register(EmployeeProxy)
class EmployeeAdmin(BaseUserConfig):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='employee')  # Показываем только сотрудников


@admin.register(DirectorProxy)
class DirectorAdmin(BaseUserConfig):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='director')  # Показываем только директоров

# ВАЖНО: Мы НЕ регистрируем основную модель User через @admin.register,
# чтобы не было дублирования. Прокси-модели заменят её в меню.