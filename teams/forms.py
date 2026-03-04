from django import forms
from .models import Team
from users.models import User


class TeamForm(forms.ModelForm):
    # Фильтруем пользователей: берем только тех, у кого role='employee'
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='employee'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Участники команды (Сотрудники)"
    )

    class Meta:
        model = Team
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название команды'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание команды'}),
        }


class AddMemberForm(forms.Form):
    """Форма добавления участника"""
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(role='employee'),
        label="Выберите сотрудника",
        widget=forms.Select(attrs={'class': 'form-control'})
    )