from django.shortcuts import render
from doctors.models import Doctor
from services.models import Service


def index(request):
    doctors = Doctor.objects.filter(
        is_available=True
    ).select_related('user')[:6]
    services = Service.objects.filter(is_active=True)[:6]
    return render(request, 'index.html', {
        'doctors': doctors,
        'services': services,
    })
