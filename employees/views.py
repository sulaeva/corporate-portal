from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User  # ← Импортируем из твоего apps users!
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date

from .models import Department, Employee, Skill, EmployeeSkill, Project, Vacation, Task
from .serializers import (
    UserRegisterSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    SkillSerializer,
    EmployeeSkillSerializer,
    ProjectSerializer,
    ProjectTeamSerializer,
    VacationSerializer,
    TaskSerializer,
)


# ==================== ПОЛЬЗОВАТЕЛЬ ====================

class UserRegisterViewSet(viewsets.ModelViewSet):
    """ViewSet для регистрации пользователей"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Пользователь успешно зарегистрирован!'
        }, status=status.HTTP_201_CREATED)


# ==================== ОТДЕЛЫ ====================

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отделами"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'office_number']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Получить всех сотрудников отдела"""
        department = self.get_object()
        employees = Employee.objects.filter(department=department)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


# ==================== СОТРУДНИКИ ====================

class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet для сотрудников (показывает всех пользователей системы)"""
    queryset = User.objects.all()  # Показываем ВСЕХ из базы Users
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Настройки поиска и фильтров под модель User
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        return Response({'detail': 'Фильтр по отделам доступен только для полной модели сотрудника'}, status=400)

    @action(detail=False, methods=['get'])
    def active(self, request):
        users = User.objects.filter(is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    # @action(detail=True, methods=['get'])
    # def skills(self, request, pk=None):
    #     """Получить навыки сотрудника"""
    #     employee = self.get_object()
    #     skills = EmployeeSkill.objects.filter(employee=employee)
    #     serializer = EmployeeSkillSerializer(skills, many=True)
    #     return Response(serializer.data)
    #
    # @action(detail=True, methods=['get'])
    # def tasks(self, request, pk=None):
    #     """Получить задачи сотрудника"""
    #     employee = self.get_object()
    #     tasks = Task.objects.filter(employee=employee)
    #     serializer = TaskSerializer(tasks, many=True)
    #     return Response(serializer.data)
    #
    # @action(detail=True, methods=['get'])
    # def vacations(self, request, pk=None):
    #     """Получить заявки на отпуск сотрудника"""
    #     employee = self.get_object()
    #     vacations = Vacation.objects.filter(employee=employee)
    #     serializer = VacationSerializer(vacations, many=True)
    #     return Response(serializer.data)


# ==================== НАВЫКИ ====================

class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet для управления навыками"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Получить навыки по категории"""
        category = request.query_params.get('category')
        if category:
            skills = Skill.objects.filter(category=category)
            serializer = self.get_serializer(skills, many=True)
            return Response(serializer.data)
        return Response({'error': 'Укажите category'}, status=400)


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    """ViewSet для управления навыками сотрудников"""
    queryset = EmployeeSkill.objects.all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'skill', 'level']
    ordering_fields = ['level']

    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Получить навыки по сотруднику"""
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            skills = EmployeeSkill.objects.filter(employee_id=employee_id)
            serializer = self.get_serializer(skills, many=True)
            return Response(serializer.data)
        return Response({'error': 'Укажите employee_id'}, status=400)


# ==================== ПРОЕКТЫ ====================

class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet для управления проектами"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить активные проекты"""
        projects = Project.objects.filter(status__in=['planning', 'in_progress'])
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Получить завершённые проекты"""
        projects = Project.objects.filter(status='completed')
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_team_member(self, request, pk=None):
        """Добавить участника в команду проекта"""
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
                project.team.add(employee)
                return Response({'message': 'Сотрудник добавлен в команду'})
            except Employee.DoesNotExist:
                return Response({'error': 'Сотрудник не найден'}, status=404)
        return Response({'error': 'Укажите employee_id'}, status=400)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить задачи проекта"""
        project = self.get_object()
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


# ==================== ОТПУСКА ====================

class VacationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заявками на отпуск"""
    queryset = Vacation.objects.all()
    serializer_class = VacationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['employee__full_name', 'reason']
    ordering_fields = ['start_date', 'created_at']

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Получить заявки на рассмотрении"""
        vacations = Vacation.objects.filter(status='pending')
        serializer = self.get_serializer(vacations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def approved(self, request):
        """Получить одобренные заявки"""
        vacations = Vacation.objects.filter(status='approved')
        serializer = self.get_serializer(vacations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Одобрить заявку на отпуск"""
        vacation = self.get_object()
        vacation.status = 'approved'
        vacation.save()
        return Response({'message': 'Заявка одобрена'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить заявку на отпуск"""
        vacation = self.get_object()
        vacation.status = 'rejected'
        vacation.save()
        return Response({'message': 'Заявка отклонена'})


# ==================== ЗАДАЧИ ====================

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для управления задачами"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'project', 'priority', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'due_date', 'created_at']

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Получить срочные задачи"""
        tasks = Task.objects.filter(priority__in=['high', 'urgent'])
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Получить просроченные задачи"""
        tasks = Task.objects.filter(due_date__lt=date.today(), status__in=['todo', 'in_progress'])
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Отметить задачу как выполненную"""
        task = self.get_object()
        task.status = 'done'
        task.completed_at = date.today()
        task.save()
        return Response({'message': 'Задача выполнена'})

    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Получить задачи по сотруднику"""
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            tasks = Task.objects.filter(employee_id=employee_id)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({'error': 'Укажите employee_id'}, status=400)