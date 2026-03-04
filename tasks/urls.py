from django.urls import path
from . import views

urlpatterns = [
    # Список всех задач
    path('', views.task_list, name='task_list'),

    # Выполненные задачи
    path('done/', views.task_done_list, name='task_done_list'),

    # Создание задачи (С НОВЫМ ВАРИАНТОМ ДЛЯ ПАРАМЕТРОВ)
    # Сначала идет путь с параметрами, чтобы Django мог его найти при редиректе
    path('create/<int:employee_id>/<int:team_id>/', views.task_create, name='task_create'),
    path('create/', views.task_create, name='task_create'),

    # Детали, редактирование, удаление, смена статуса
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('<int:pk>/status/<str:new_status>/', views.task_change_status, name='task_change_status'),

    # Страница задач сотрудника в контексте команды
    path('employee/<int:employee_id>/team/<int:team_id>/', views.employee_tasks, name='employee_tasks'),
]