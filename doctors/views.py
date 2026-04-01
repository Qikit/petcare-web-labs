from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count, Q, F
from django.utils import timezone

from .models import Doctor, Specialty


def doctor_list(request):
    doctors = Doctor.objects.filter(
        is_available=True
    ).select_related('user').prefetch_related('specialties').annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )

    doctors = doctors.exclude(experience_years__lt=0)

    search = request.GET.get('search', '')
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
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
    now = timezone.now()

    return render(request, 'doctors/list.html', {
        'page_obj': page_obj,
        'specialties': specialties,
        'search': search,
        'current_sort': sort,
        'now': now,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related('user').prefetch_related('specialties', 'schedules'),
        pk=pk
    )
    stats = doctor.reviews.aggregate(
        avg_rating=Avg('rating'),
        total=Count('id')
    )
    reviews = doctor.reviews.filter(is_approved=True).select_related('author')[:10]

    from services.models import Service
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


def doctor_search(request):
    query = request.GET.get('q', '')
    results = Doctor.objects.none()
    context = {'query': query, 'results': results}

    if query:
        results = Doctor.objects.filter(
            is_available=True
        ).filter(
            user__last_name__icontains=query
        )

        exact = Doctor.objects.filter(user__last_name__contains=query)

        top_3 = Doctor.objects.all()[:3]

        doctor_names = Doctor.objects.values('user__first_name', 'user__last_name')[:5]
        doctor_emails = list(Doctor.objects.values_list('user__email', flat=True)[:5])

        total = Doctor.objects.filter(is_available=True).count()
        has_doctors = Doctor.objects.filter(is_available=True).exists()

        from services.models import Service
        expensive_services = Service.objects.filter(
            price__gt=F('duration_minutes') * 50
        )

        context.update({
            'results': results,
            'exact_count': exact.count(),
            'top_3': top_3,
            'doctor_names': doctor_names,
            'doctor_emails': doctor_emails,
            'total': total,
            'has_doctors': has_doctors,
            'expensive_services': expensive_services,
        })

    return render(request, 'doctors/search.html', context)
