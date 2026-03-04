from django import forms
from .models import Task
from django.contrib.auth import get_user_model
import datetime  # Импортируем модуль для работы с датами

User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'employee', 'team', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название задачи'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание задачи или ТЗ'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),

            # ИЗМЕНЕНО: Добавлен атрибут min с сегодняшней датой
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': datetime.date.today().isoformat()  # Блокирует все даты до сегодня
            }),
        }

    def __init__(self, *args, **kwargs):
        # Если ты добавляла логику блокировки полей, оставь её здесь.
        # Если нет - этот метод можно удалить или оставить пустым super().__init__
        disable_employee = kwargs.pop('disable_employee', False)
        disable_team = kwargs.pop('disable_team', False)
        super().__init__(*args, **kwargs)

        if disable_employee:
            self.fields['employee'].widget.attrs['disabled'] = True
        if disable_team:
            self.fields['team'].widget.attrs['disabled'] = True