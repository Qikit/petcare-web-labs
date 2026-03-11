from django import forms
from .models import Pet


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ('name', 'species', 'breed', 'age', 'weight', 'health_notes', 'photo')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кличка'}),
            'species': forms.Select(attrs={'class': 'form-control'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Порода'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Возраст в месяцах'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'health_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Кличка питомца',
            'health_notes': 'Особенности здоровья',
        }
        help_texts = {
            'age': 'Укажите возраст в месяцах',
            'weight': 'Вес в килограммах',
        }
        error_messages = {
            'name': {'required': 'Укажите кличку питомца'},
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError('Кличка должна содержать минимум 2 символа')
        return name.strip().title()

    def save(self, commit=True):
        pet = super().save(commit=False)
        if not pet.breed:
            pet.breed = 'Не указана'
        if commit:
            pet.save()
        return pet
