from rest_framework import serializers
from users.models import User
from .models import Department, Employee, Skill, EmployeeSkill, Project, Vacation
from tasks.models import Task
from teams.models import Team


# ==================== ПОЛЬЗОВАТЕЛЬ ====================

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='employee', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role', 'first_name', 'last_name']
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
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'employee')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        user.role = role
        if role == 'director':
            user.is_staff = True
        user.save()

        return user


# ==================== ОТДЕЛЫ ====================

class DepartmentSerializer(serializers.ModelSerializer):
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
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'position', 'is_active', 'date_joined'
        ]
        read_only_fields = ['date_joined', 'full_name']

    def get_full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


# ==================== НАВЫКИ ====================

class SkillSerializer(serializers.ModelSerializer):
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description', 'employees_count']
        read_only_fields = ['employees_count']

    def get_employees_count(self, obj):
        return obj.employees.count()  # ← исправлено

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Название навыка должно быть минимум 2 символа!")
        return value


class EmployeeSkillSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'employee', 'employee_name', 'skill', 'skill_name', 'level', 'level_display']

    def validate(self, data):
        if EmployeeSkill.objects.filter(employee=data['employee'], skill=data['skill']).exists():
            raise serializers.ValidationError("Этот навык уже добавлен сотруднику!")
        return data


# ==================== ПРОЕКТЫ ====================

class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
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

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.username
        return None

    def get_team_count(self, obj):
        return obj.team.count()

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название проекта должно быть минимум 3 символа!")
        return value

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] and data['end_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала!")
        return data


class ProjectTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['team']


# ==================== ОТПУСКА ====================

class VacationSerializer(serializers.ModelSerializer):
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
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала!")
            from datetime import date
            if data['start_date'] < date.today():
                raise serializers.ValidationError("Дата начала не может быть в прошлом!")
        return data


# ==================== ЗАДАЧИ ====================

class TaskSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    # ✅ Только директор и менеджер могут быть создателем задачи
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['director', 'manager']),
        required=False,
        allow_null=True
    )

    # ✅ Только сотрудники могут быть исполнителями
    employee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='employee')
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'employee', 'employee_name',
            'manager', 'manager_name', 'team',
            'priority', 'status', 'due_date', 'created_at'
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.username
        return None


# ==================== КОМАНДЫ ====================

class TeamSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['director', 'manager'])
    )
    manager_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    members_detail = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description',
            'manager', 'manager_name',
            'members', 'members_detail', 'members_count',
            'created_at'
        ]

    def get_manager_name(self, obj):
        return obj.manager.get_full_name() or obj.manager.username

    def get_members_count(self, obj):
        return obj.members.count()

    def get_members_detail(self, obj):
        return [
            {
                'id': m.id,
                'username': m.username,
                'full_name': m.get_full_name() or m.username,
                'role': m.get_role_display(),
                'position': m.position or '—'
            }
            for m in obj.members.all()
        ]

    def validate_manager(self, value):
        if value.role == 'employee':
            raise serializers.ValidationError("Сотрудник не может быть менеджером команды!")
        return value


# ==================== ДЛЯ АДМИНКИ ====================

class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'email', 'position', 'department_name']


# ==================== ДЛЯ НОВОЙ СИСТЕМЫ (роли) ====================

class UserSerializer(serializers.ModelSerializer):
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