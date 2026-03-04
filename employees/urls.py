from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegisterViewSet,
    DepartmentViewSet,
    EmployeeViewSet,
    SkillViewSet,
    EmployeeSkillViewSet,
    ProjectViewSet,
    VacationViewSet,
    TaskViewSet,
)

# Создаём роутер
router = DefaultRouter()
router.register(r'register', UserRegisterViewSet, basename='register')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'employee-skills', EmployeeSkillViewSet, basename='employee-skill')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'vacations', VacationViewSet, basename='vacation')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]