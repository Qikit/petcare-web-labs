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


@register.simple_tag
def doctor_photo_url(doctor):
    """Возвращает URL фото врача либо стоковый аватар по pk."""
    if doctor.photo:
        return doctor.photo.url
    seed = (doctor.pk * 7) % 70 + 1
    return f'https://i.pravatar.cc/400?img={seed}'


@register.simple_tag
def service_photo_url(service):
    """Возвращает URL фото услуги либо стоковую картинку по pk."""
    if service.photo:
        return service.photo.url
    return f'https://picsum.photos/seed/svc{service.pk}/600/360'


SPECIALTY_ICONS = {
    'Терапия': 'bi-clipboard2-pulse',
    'Хирургия': 'bi-scissors',
    'Офтальмология': 'bi-eye',
    'Дерматология': 'bi-droplet-half',
    'Стоматология': 'bi-emoji-smile',
    'Кардиология': 'bi-heart-pulse',
    'Гастроэнтерология': 'bi-egg-fried',
    'Неврология': 'bi-lightning-charge',
    'Урология': 'bi-droplet',
    'Эндокринология': 'bi-eyedropper',
}


@register.simple_tag
def spec_icon(name):
    """Возвращает CSS-класс Bootstrap-иконки по названию специализации."""
    return SPECIALTY_ICONS.get(name, 'bi-bookmark-heart')


@register.simple_tag
def pet_photo_url(pet):
    """Возвращает URL фото питомца либо стоковую картинку по виду."""
    if pet.photo:
        return pet.photo.url
    species_seeds = {
        'cat': 'cat',
        'dog': 'dog',
        'bird': 'bird',
        'rodent': 'hamster',
        'reptile': 'lizard',
        'other': 'animal',
    }
    seed = species_seeds.get(pet.species, 'animal')
    return f'https://picsum.photos/seed/{seed}{pet.pk}/600/400'
