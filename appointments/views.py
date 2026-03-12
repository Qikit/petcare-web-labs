from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Appointment
from .forms import AppointmentForm


@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            messages.success(request, 'Запись создана успешно')
            return redirect('appointment-list')
    else:
        form = AppointmentForm(request.user)
        doctor_id = request.GET.get('doctor')
        if doctor_id:
            form.fields['doctor'].initial = doctor_id
    return render(request, 'appointments/create.html', {'form': form})


@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(
        client=request.user
    ).select_related('doctor__user', 'pet', 'service').order_by('-date')
    return render(request, 'appointments/list.html', {'appointments': appointments})


@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    if request.method == 'POST' and appointment.can_cancel():
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancel_reason = request.POST.get('reason', '')
        appointment.save()
        messages.success(request, 'Запись отменена')
    return redirect('appointment-list')
