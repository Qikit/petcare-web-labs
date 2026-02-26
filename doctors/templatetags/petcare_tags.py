from django import template
from django.db.models import Avg, Count

from doctors.models import Doctor
from reviews.models import Review

register = template.Library()


@register.simple_tag
def total_doctors():
    """Простой шаблонный тег — возвращает кол-во доступных врачей"""
    return Doctor.objects.filter(is_available=True).count()


@register.simple_tag(takes_context=True)
def get_user_viewed_doctors(context):
    """Шаблонный тег с контекстными переменными — недавно просмотренные врачи"""
    request = context.get('request')
    if not request:
        return Doctor.objects.none()
    viewed_ids = request.session.get('viewed_doctors', [])
    return Doctor.objects.filter(pk__in=viewed_ids).select_related('user')


@register.inclusion_tag('includes/latest_reviews.html')
def show_latest_reviews(count=5):
    """Шаблонный тег, возвращающий набор запросов — последние одобренные отзывы"""
    reviews = Review.approved.select_related('author', 'doctor__user')[:count]
    return {'latest_reviews': reviews}
