from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Расширенная модель пользователя с ролями"""

    ROLE_CHOICES = [
        ('director', 'Директор'),
        ('manager', 'Менеджер'),
        ('employee', 'Сотрудник'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name="Роль"
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    position = models.CharField(max_length=100, verbose_name="Должность", blank=True)
    department = models.ForeignKey(
        'employees.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Отдел"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_director(self):
        return self.role == 'director'

    def is_manager(self):
        return self.role == 'manager'

    def is_employee(self):
        return self.role == 'employee'