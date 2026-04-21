from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о вашем опыте...',
            }),
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Текст отзыва',
        }
        help_texts = {
            'rating': 'Оценка от 1 до 5',
        }
        error_messages = {
            'rating': {'required': 'Поставьте оценку'},
            'text': {'required': 'Напишите отзыв'},
        }
