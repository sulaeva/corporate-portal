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
    TeamViewSet,
)

from . import views_skills
from . import views_meetings



router = DefaultRouter()
router.register(r'register', UserRegisterViewSet, basename='register')
# router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'employee-skills', EmployeeSkillViewSet, basename='employee-skill')
# router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'vacations', VacationViewSet, basename='vacation')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ Сайтовая часть навыков — отдельные префиксы чтобы не конфликтовать с API
    path('skills-list/', views_skills.skills_list, name='skills_list'),
    path('skills-add/', views_skills.skill_add, name='skill_add'),
    path('skills-detail/<int:pk>/', views_skills.skill_detail, name='skill_detail'),
    path('skills-delete/<int:pk>/', views_skills.skill_delete, name='skill_delete'),
    path('skills-assign/<int:pk>/', views_skills.skill_assign, name='skill_assign'),

    path('meetings/', views_meetings.meeting_list, name='meeting_list'),
    path('meetings/create/', views_meetings.meeting_create, name='meeting_create'),
    path('meetings/delete/<int:pk>/', views_meetings.meeting_delete, name='meeting_delete'),
    path('meetings/<int:pk>/read/', views_meetings.meeting_read, name='meeting_read'),
]