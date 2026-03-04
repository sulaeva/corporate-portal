from django.db import models
from django.conf import settings


class Team(models.Model):
    """Модель команды"""

    name = models.CharField(max_length=100, verbose_name="Название команды")
    description = models.TextField(blank=True, verbose_name="Описание")
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_teams',
        verbose_name="Менеджер команды"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True,
        verbose_name="Участники"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()