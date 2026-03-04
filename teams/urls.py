from django.urls import path
from . import views

urlpatterns = [
    # --- Основные пути ---
    path('', views.my_teams_list, name='my_teams_list'),  # Список команд
    path('my-teams/', views.my_teams_list, name='team_list'),  # Альтернативное имя для списка
    path('create/', views.team_create, name='team_create'),  # Создание


    path('<int:pk>/delete/', views.team_delete, name='team_delete'),  # !!! НОВЫЙ ПУТЬ ДЛЯ УДАЛЕНИЯ !!!

    path('<int:pk>/', views.team_delete, name='team_detail'),  # Детали команды
    path('my-teams/<int:pk>/', views.team_delete, name='team_detail_alt'),
    # Детали с префиксом (добавил _alt, чтобы имена не совпадали)

    # --- Действия с участниками ---
    path('<int:pk>/add-member/', views.my_teams_list, name='team_add_member'),
    path('<int:team_pk>/remove-member/<int:user_pk>/', views.my_teams_list, name='team_remove_member'),
]