from rest_framework import serializers
from users.models import User  # ← ✅ ИМПОРТИРУЕМ ИЗ ТВОЕГО APPS USERS!
from .models import Department, Employee, Skill, EmployeeSkill, Project, Vacation, Task


# ==================== ПОЛЬЗОВАТЕЛЬ ====================

class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    # Добавляем роль (если она есть в твоей модели User)
    # Если поле role нет в модели User, удали эту строку и её обработку в create()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='employee', required=False)

    class Meta:
        model = User
        # ДОБАВЛЕНО: first_name и last_name
        # УБРАНО: phone и position (их нет в стандартной модели User, это вызовет ошибку)
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'role',
            'first_name',
            'last_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают!")
        if len(data['password']) < 8:
            raise serializers.ValidationError("Пароль должен быть минимум 8 символов!")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует!")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует!")
        return data

    def create(self, validated_data):
        # Удаляем поле подтверждения пароля, оно не нужно для сохранения
        validated_data.pop('password_confirm')

        # Извлекаем роль, если она была передана
        role = validated_data.pop('role', 'employee')

        # Создаем пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Если у твоей модели User есть поле 'role', раскомментируй следующую строку:
        # user.role = role
        # user.save()

        return user


# ==================== ОТДЕЛЫ ====================

class DepartmentSerializer(serializers.ModelSerializer):
    """Сериализатор отдела"""
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'office_number', 'employees_count', 'created_at']
        read_only_fields = ['created_at']

    def get_employees_count(self, obj):
        return obj.employees.count()

    def validate_code(self, value):
        if not value.isupper():
            raise serializers.ValidationError("Код отдела должен быть заглавными буквами!")
        return value

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название отдела должно быть минимум 3 символа!")
        return value


# ==================== СОТРУДНИКИ ====================

class EmployeeSerializer(serializers.ModelSerializer):
    # Добавляем поле full_name виртуально, объединяя имя и фамилию
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Теперь поля соответствуют модели User + наше виртуальное поле
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_active', 'date_joined']

    def get_full_name(self, obj):
        # Возвращаем "Имя Фамилия" или просто username, если имени нет
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


# ==================== НАВЫКИ ====================

class SkillSerializer(serializers.ModelSerializer):
    """Сериализатор навыка"""
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description', 'employees_count']
        read_only_fields = ['employees_count']

    def get_employees_count(self, obj):
        return obj.employeeskill_set.count()

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Название навыка должно быть минимум 2 символа!")
        return value


class EmployeeSkillSerializer(serializers.ModelSerializer):
    """Сериализатор связи сотрудник-навык"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = [
            'id', 'employee', 'employee_name', 'skill', 'skill_name',
            'level', 'level_display'
        ]

    def validate(self, data):
        # Проверка на дубликат
        if EmployeeSkill.objects.filter(
            employee=data['employee'],
            skill=data['skill']
        ).exists():
            raise serializers.ValidationError("Этот навык уже добавлен сотруднику!")
        return data


# ==================== ПРОЕКТЫ ====================

class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    team_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'status_display', 'manager', 'manager_name',
            'team', 'team_count', 'created_at'
        ]
        read_only_fields = ['created_at', 'status_display', 'manager_name', 'team_count']

    def get_team_count(self, obj):
        return obj.team.count()

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название проекта должно быть минимум 3 символа!")
        return value

    def validate(self, data):
        # Проверка дат
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] and data['end_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала!")
        return data


class ProjectTeamSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления команды в проект"""
    class Meta:
        model = Project
        fields = ['team']


# ==================== ОТПУСКА ====================

class VacationSerializer(serializers.ModelSerializer):
    """Сериализатор заявки на отпуск"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = Vacation
        fields = [
            'id', 'employee', 'employee_name', 'start_date', 'end_date',
            'status', 'status_display', 'reason', 'duration_days', 'created_at'
        ]
        read_only_fields = ['created_at', 'status_display', 'employee_name', 'duration_days']

    def get_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    def validate(self, data):
        # Проверка дат
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала!")
            # Проверка на будущее
            from datetime import date
            if data['start_date'] < date.today():
                raise serializers.ValidationError("Дата начала не может быть в прошлом!")
        return data


# ==================== ЗАДАЧИ ====================

class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'employee', 'employee_name',
            'project', 'project_name', 'priority', 'priority_display',
            'status', 'status_display', 'due_date', 'created_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'completed_at', 'priority_display', 'status_display', 'employee_name', 'project_name']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Название задачи должно быть минимум 5 символов!")
        return value

    def validate(self, data):
        # Проверка дат
        if 'due_date' in data and data['due_date']:
            from datetime import date
            if data['due_date'] < date.today():
                raise serializers.ValidationError("Срок выполнения не может быть в прошлом!")
        return data


# ==================== ДЛЯ АДМИНКИ (краткие версии) ====================

class DepartmentListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка отделов"""
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка сотрудников"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'email', 'position', 'department_name']


# ==================== ДЛЯ НОВОЙ СИСТЕМЫ (роли) ====================

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для API"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'position',
            'department', 'department_name', 'is_active'
        ]
        read_only_fields = ['role_display', 'department_name']