from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from employees.models import Department, Skill


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) ...'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        required=False, label="Отдел",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Без отдела"
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        label="Навыки",
        widget=forms.CheckboxSelectMultiple
    )
    skill_level = forms.ChoiceField(
        choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        required=False,
        label="Уровень владения",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # ✅ Директор убран из регистрации
    role = forms.ChoiceField(
        choices=[('manager', 'Менеджер'), ('employee', 'Сотрудник')],
        required=True,
        label="Роль в системе",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  'role', 'phone', 'department', 'skills', 'skill_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['department'].queryset = Department.objects.all()
        except Exception:
            self.fields['department'].queryset = Department.objects.none()
        try:
            self.fields['skills'].queryset = Skill.objects.all().order_by('category', 'name')
        except Exception:
            self.fields['skills'].queryset = Skill.objects.none()

        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Придумайте пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Повторите пароль'})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Логин'})