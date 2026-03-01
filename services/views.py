from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Service
from doctors.models import Specialty


def service_list(request):
    services = Service.objects.filter(
        is_active=True
    ).select_related('specialty').order_by('name')

    search = request.GET.get('search', '')
    if search:
        services = services.filter(name__icontains=search)

    specialty_id = request.GET.get('specialty')
    if specialty_id:
        services = services.filter(specialty__id=specialty_id)

    paginator = Paginator(services, 9)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    specialties = Specialty.objects.all()

    return render(request, 'services/list.html', {
        'page_obj': page_obj,
        'specialties': specialties,
        'search': search,
    })
