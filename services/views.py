from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render

from doctors.models import Doctor, Specialty
from .forms import ServiceForm
from .models import Service


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


def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('specialty'),
        pk=pk,
    )
    if service.specialty_id:
        related_doctors = (
            Doctor.objects
            .filter(is_available=True, specialties=service.specialty)
            .select_related('user')
        )
    else:
        related_doctors = Doctor.objects.none()
    return render(request, 'services/detail.html', {
        'service': service,
        'related_doctors': related_doctors,
    })


@staff_member_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Услуга «{service.name}» создана')
            return redirect('service-detail', pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, 'services/form.html', {
        'form': form,
        'title': 'Добавить услугу',
    })


@staff_member_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга обновлена')
            return redirect('service-detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/form.html', {
        'form': form,
        'title': f'Редактировать «{service.name}»',
        'service': service,
    })


@staff_member_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        name = service.name
        service.delete()
        messages.success(request, f'Услуга «{name}» удалена')
        return redirect('service-list')
    return render(request, 'services/confirm_delete.html', {'service': service})
