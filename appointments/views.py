from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Appointment, MedicalRecord
from .forms import AppointmentForm
import io


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


@login_required
def medical_record_pdf(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    p.setFont('Helvetica-Bold', 18)
    p.drawString(50, height - 50, 'PetCare')

    p.setFont('Helvetica', 12)
    p.drawString(50, height - 80, f'Medical Record #{record.pk}')
    p.drawString(50, height - 110, f'Date: {record.created_at.strftime("%d.%m.%Y")}')

    p.drawString(50, height - 150, f'Pet: {record.pet.name} ({record.pet.get_species_display()})')
    p.drawString(50, height - 170, f'Doctor: {record.doctor.user.get_full_name()}')

    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, height - 210, 'Diagnosis:')
    p.setFont('Helvetica', 11)
    y = height - 230
    for line in record.diagnosis.split('\n'):
        p.drawString(70, y, line[:80])
        y -= 18

    if record.treatment:
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, y - 10, 'Treatment:')
        p.setFont('Helvetica', 11)
        y -= 30
        for line in record.treatment.split('\n'):
            p.drawString(70, y, line[:80])
            y -= 18

    if record.recommendations:
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, y - 10, 'Recommendations:')
        p.setFont('Helvetica', 11)
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
