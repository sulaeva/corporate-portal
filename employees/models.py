from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отдела")
    code = models.CharField(max_length=10, unique=True, verbose_name="Код отдела")
    office_number = models.CharField(max_length=20, verbose_name="Номер кабинета")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Employee(models.Model):
    POSITION_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Team Lead'),
        ('manager', 'Manager'),
    ]

    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='junior', verbose_name="Должность")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True,
        related_name='employees', verbose_name="Отдел"
    )
    hire_date = models.DateField(verbose_name="Дата приема")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name}"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('framework', 'Framework'),
        ('database', 'Database'),
        ('soft_skills', 'Soft Skills'),
        ('language', 'Language'),
        ('tools', 'Tools'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название навыка")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ['name']

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    LEVEL_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='employees')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='basic')

    class Meta:
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"
        unique_together = ['employee', 'skill']

    def __str__(self):
        return f"{self.employee.username} - {self.skill.name} ({self.level})"


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='managed_projects', verbose_name="Менеджер проекта"
    )
    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Vacation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='vacations', verbose_name="Сотрудник"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, verbose_name="Причина")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заявка на отпуск"
        verbose_name_plural = "Заявки на отпуск"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.username} - {self.start_date} до {self.end_date}"

class Meeting(models.Model):
    title = models.CharField(max_length=200, verbose_name="Тема встречи")
    description = models.TextField(blank=True, verbose_name="Описание")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    location = models.CharField(max_length=200, blank=True, verbose_name="Место")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='organized_meetings', verbose_name="Организатор"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='meetings', blank=True,
        verbose_name="Участники"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} — {self.date} {self.time}"

class MeetingRead(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='meeting_reads'
    )
    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE,
        related_name='reads'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'meeting']