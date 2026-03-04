from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from employees.models import Department


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) ...'})
    )
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Должность'})
    )

    # Объявляем поле отдела, но БЕЗ queryset на уровне класса
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # Пустой запрос по умолчанию
        required=False,
        label="Отдел",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Без отдела"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone', 'position', 'department']
        # Добавил 'department' сюда, чтобы оно точно сохранилось

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Безопасное получение отделов только при создании формы
        try:
            self.fields['department'].queryset = Department.objects.all()
        except Exception:
            # Если таблица еще не создана, оставляем пустым, чтобы не ломать сервер
            self.fields['department'].queryset = Department.objects.none()

        # 2. Применяем стили к полям пароля
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

        # 3. Применяем стили к полю username (если вдруг не применились автоматически)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Логин'})

        # 4. Если роль должна выбираться из списка, убедимся, что виджет корректен
        if 'role' in self.fields:
            self.fields['role'].widget.attrs.update({'class': 'form-select'})