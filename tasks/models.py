from django.db import models
from django.conf import settings

class Task(models.Model):
    """Модель задачи"""

    STATUS_CHOICES = [
        ('todo', 'Новая'),
        ('inprogress', 'В работе'),
        ('done', 'Выполнено'),  # <-- Важно: первое значение в скобках
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)

    # Кто выполняет задачу (Исполнитель)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name="Исполнитель"
    )

    # Кто создал задачу (Менеджер/Директор) - НОВОЕ ПОЛЕ
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_tasks',
        verbose_name="Менеджер (создатель)"
    )

    # Команда (если есть приложение teams)
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Команда"
    )

    # Основные поля
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        "Приоритет",
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    due_date = models.DateField("Срок выполнения", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return self.title

    def can_change_status(self, user):
        # Менять статус может исполнитель, создатель (менеджер) или директор
        return user == self.employee or user == self.manager or getattr(user, 'role', '') == 'director'

    def can_advance_status(self):
        return self.status != 'done'