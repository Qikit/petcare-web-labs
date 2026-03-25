from django.contrib import admin

from .models import Appointment, MedicalRecord


class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'client', 'doctor', 'service', 'date', 'status', 'show_is_upcoming')
    list_display_links = ('__str__',)
    list_filter = ('status', 'date')
    search_fields = ('client__email', 'doctor__user__last_name', 'pet__name')
    raw_id_fields = ('client', 'doctor', 'pet', 'service')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    inlines = [MedicalRecordInline]

    @admin.display(description='Предстоит', boolean=True)
    def show_is_upcoming(self, obj):
        return obj.is_upcoming()

    @admin.action(description='Экспортировать в PDF')
    def export_pdf(self, request, queryset):
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buf = io.BytesIO()
        p = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont('Helvetica-Bold', 16)
        p.drawString(50, y, 'PetCare - Appointments Export')
        y -= 40

        p.setFont('Helvetica', 10)
        for apt in queryset:
            if y < 50:
                p.showPage()
                y = height - 50
            p.drawString(50, y, f'{apt.date} | {apt.client} | {apt.doctor} | {apt.service} | {apt.get_status_display()}')
            y -= 18

        p.showPage()
        p.save()
        buf.seek(0)

        response = HttpResponse(buf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="appointments.pdf"'
        return response

    actions = ['export_pdf']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pet', 'doctor', 'show_diagnosis_short', 'created_at')
    search_fields = ('diagnosis', 'treatment', 'pet__name')
    raw_id_fields = ('appointment', 'pet', 'doctor')
    readonly_fields = ('created_at',)

    @admin.display(description='Диагноз (кратко)')
    def show_diagnosis_short(self, obj):
        if len(obj.diagnosis) > 80:
            return obj.diagnosis[:80] + '...'
        return obj.diagnosis
