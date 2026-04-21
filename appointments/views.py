import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import AppointmentForm
from .models import Appointment, MedicalRecord
from .pdf_utils import register_fonts


@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            messages.success(request, 'Запись создана успешно')
            return redirect('appointment-list')
    else:
        form = AppointmentForm(user=request.user)
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


@login_required
def medical_record_pdf(request, pk):
    record = get_object_or_404(
        MedicalRecord.objects.select_related('pet', 'doctor__user'),
        pk=pk,
        pet__owner=request.user,
    )

    font_regular, font_bold = register_fonts()

    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    p.setFont(font_bold, 18)
    p.drawString(50, height - 50, 'PetCare')

    p.setFont(font_regular, 12)
    p.drawString(50, height - 80, f'Медицинская карта №{record.pk}')
    p.drawString(50, height - 110, f'Дата: {record.date.strftime("%d.%m.%Y")}')

    p.drawString(50, height - 150, f'Питомец: {record.pet.name} ({record.pet.get_species_display()})')
    p.drawString(50, height - 170, f'Врач: {record.doctor.user.get_full_name()}')

    p.setFont(font_bold, 12)
    p.drawString(50, height - 210, 'Диагноз:')
    p.setFont(font_regular, 11)
    y = height - 230
    for line in record.diagnosis.split('\n'):
        p.drawString(70, y, line[:80])
        y -= 18

    if record.treatment:
        p.setFont(font_bold, 12)
        p.drawString(50, y - 10, 'Лечение:')
        p.setFont(font_regular, 11)
        y -= 30
        for line in record.treatment.split('\n'):
            p.drawString(70, y, line[:80])
            y -= 18

    if record.recommendations:
        p.setFont(font_bold, 12)
        p.drawString(50, y - 10, 'Рекомендации:')
        p.setFont(font_regular, 11)
        y -= 30
        for line in record.recommendations.split('\n'):
            p.drawString(70, y, line[:80])
            y -= 18

    p.showPage()
    p.save()
    buf.seek(0)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="record_{record.pk}.pdf"'
    return response
