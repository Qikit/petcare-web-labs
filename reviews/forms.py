from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    text = forms.CharField(
        label='Текст отзыва',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Расскажите о вашем опыте...',
        })
    )

    class Meta:
        model = Review
        fields = ('rating', 'text')
        exclude = ('is_approved',)
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
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

    class Media:
        css = {'all': ('css/style.css',)}
