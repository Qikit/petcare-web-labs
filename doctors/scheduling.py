from datetime import datetime, timedelta

from django.utils import timezone


def get_available_slots(doctor, days_ahead=7, slot_minutes=30):
    """
    Возвращает свободные временные слоты у врача на ближайшие N дней.
    Учитывает расписание (Schedule), активные приёмы (кроме cancelled)
    и текущее время — прошедшие сегодня слоты не предлагаются.

    :return: list[dict] вида [{'date': date, 'time': time}, ...]
    """
    from appointments.models import Appointment

    now = timezone.localtime()
    today = now.date()
    end_date = today + timedelta(days=days_ahead)

    schedules_by_day = {s.day_of_week: s for s in doctor.schedules.all()}

    busy = set(
        Appointment.objects
        .filter(doctor=doctor, date__gte=today, date__lte=end_date)
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list('date', 'time_slot')
    )

    result = []
    current = today
    while current <= end_date:
        sched = schedules_by_day.get(current.weekday())
        if sched:
            slot_dt = datetime.combine(current, sched.start_time)
            end_dt = datetime.combine(current, sched.end_time)
            while slot_dt + timedelta(minutes=slot_minutes) <= end_dt:
                slot_t = slot_dt.time()
                if current == today and slot_t <= now.time():
                    slot_dt += timedelta(minutes=slot_minutes)
                    continue
                if (current, slot_t) not in busy:
                    result.append({'date': current, 'time': slot_t})
                slot_dt += timedelta(minutes=slot_minutes)
        current += timedelta(days=1)

    return result
