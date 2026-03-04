from django.urls import path
from . import views

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
]
