from django.db.models import Avg, Count, Q
from django.shortcuts import render

from appointments.models import Appointment
from doctors.models import Doctor, Specialty
from reviews.models import Review
from services.models import Service


def index(request):
    top_doctors = (
        Doctor.objects
        .filter(is_available=True)
        .annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews'),
        )
        .exclude(avg_rating=None)
        .order_by('-avg_rating')
        .select_related('user')[:5]
    )

    popular_services = (
        Service.objects
        .filter(is_active=True)
        .annotate(popularity=Count('appointments'))
        .order_by('-popularity', 'name')[:5]
    )

    latest_reviews = (
        Review.objects
        .filter(is_approved=True)
        .select_related('author', 'doctor__user')
        .order_by('-created_at')[:3]
    )

    specialties = (
        Specialty.objects
        .annotate(doctors_count=Count('doctors'))
        .exclude(doctors_count=0)
        .order_by('-doctors_count', 'name')[:6]
    )

    stats = {
        'doctors_total': Doctor.objects.filter(is_available=True).count(),
        'services_total': Service.objects.filter(is_active=True).count(),
        'completed_appointments': Appointment.objects
            .filter(status=Appointment.Status.COMPLETED).count(),
        'specialties_total': Specialty.objects.count(),
    }

    return render(request, 'index.html', {
        'top_doctors': top_doctors,
        'popular_services': popular_services,
        'latest_reviews': latest_reviews,
        'specialties': specialties,
        'stats': stats,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    doctors = []
    services = []
    specialties = []

    if query:
        doctors = (
            Doctor.objects
            .filter(is_available=True)
            .filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(bio__icontains=query)
            )
            .select_related('user')
            .distinct()[:10]
        )
        services = (
            Service.objects
            .filter(is_active=True)
            .filter(Q(name__icontains=query) | Q(description__icontains=query))[:10]
        )
        specialties = (
            Specialty.objects
            .filter(Q(name__icontains=query) | Q(description__icontains=query))[:10]
        )

    return render(request, 'search.html', {
        'query': query,
        'doctors': doctors,
        'services': services,
        'specialties': specialties,
    })
