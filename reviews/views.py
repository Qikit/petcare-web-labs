from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from appointments.models import Appointment
from .forms import ReviewForm


@login_required
def review_create(request, appointment_pk):
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_pk,
        client=request.user,
        status=Appointment.Status.COMPLETED,
    )

    if hasattr(appointment, 'review'):
        messages.info(request, 'Отзыв на этот приём уже оставлен')
        return redirect('doctor-detail', pk=appointment.doctor_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.doctor = appointment.doctor
            review.appointment = appointment
            review.save()
            messages.success(request, 'Спасибо за отзыв! Он появится после модерации.')
            return redirect('doctor-detail', pk=appointment.doctor_id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/form.html', {
        'form': form,
        'doctor': appointment.doctor,
        'appointment': appointment,
    })
