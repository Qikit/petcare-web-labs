from django.core.management.base import BaseCommand

from reviews.models import Review


class Command(BaseCommand):
    help = 'Удаляет отзывы без привязанного приёма (данные до security-фикса)'

    def handle(self, *args, **options):
        orphans = Review.objects.filter(appointment__isnull=True)
        count = orphans.count()
        orphans.delete()
        self.stdout.write(self.style.SUCCESS(f'Удалено осиротевших отзывов: {count}'))
