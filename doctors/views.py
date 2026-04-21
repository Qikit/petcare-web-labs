from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from services.models import Service
from .models import Doctor, Specialty


def doctor_list(request):
    doctors = Doctor.objects.filter(
        is_available=True,
    ).select_related('user').prefetch_related('specialties').annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews'),
    )

    search = request.GET.get('search', '')
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
        )

    specialty_id = request.GET.get('specialty')
    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)

    sort = request.GET.get('sort', 'experience')
    if sort == 'rating':
        doctors = doctors.order_by('-avg_rating')
    elif sort == 'price':
        doctors = doctors.order_by('consultation_price')
    else:
        doctors = doctors.order_by('-experience_years')

    paginator = Paginator(doctors, 6)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    specialties = Specialty.objects.all()

    return render(request, 'doctors/list.html', {
        'page_obj': page_obj,
        'specialties': specialties,
        'search': search,
        'current_sort': sort,
        'now': timezone.now(),
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.prefetch_related('specialties', 'schedules'),
        pk=pk,
    )
    stats = doctor.reviews.aggregate(
        avg_rating=Avg('rating'),
        total=Count('id'),
    )
    reviews = doctor.reviews.filter(is_approved=True).select_related('author')[:10]

    spec_ids = doctor.specialties.values_list('id', flat=True)
    doctor_services = Service.objects.filter(specialty__id__in=spec_ids, is_active=True)

    viewed = request.session.get('viewed_doctors', [])
    if doctor.pk not in viewed:
        viewed.append(doctor.pk)
        request.session['viewed_doctors'] = viewed[-10:]

    return render(request, 'doctors/detail.html', {
        'doctor': doctor,
        'stats': stats,
        'reviews': reviews,
        'services': doctor_services,
    })
