from django.urls import path
from . import views
from . import views_vacation

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Главный роутер
    path('', views.dashboard, name='dashboard'),

    # Конкретные дашборды
    path('dashboard/director/', views.dashboard_director, name='dashboard_director'),
    path('dashboard/manager/', views.dashboard_manager, name='dashboard_manager'),
    path('dashboard/employee/', views.dashboard_employee, name='dashboard_employee'),

    path('users/', views.users_list, name='users_list'),       # Для "Всего в системе"
    path('staff/', views.staff_list, name='staff_list'),
    path('search/', views.global_search, name='global_search'),
    path('profile/', views.profile, name='profile'),


    path('vacation/request/', views_vacation.vacation_request, name='vacation_request'),
    path('vacation/my/', views_vacation.my_vacations, name='my_vacations'),
    path('vacation/all/', views_vacation.vacation_list, name='vacation_list'),
    path('vacation/<int:pk>/approve/', views_vacation.vacation_approve, name='vacation_approve'),
    path('vacation/<int:pk>/reject/', views_vacation.vacation_reject, name='vacation_reject'),
]
