from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **options):
        from users.models import User
        from doctors.models import Specialty, Doctor, DoctorSpecialty, Schedule
        from pets.models import Pet
        from services.models import Service
        from appointments.models import Appointment, MedicalRecord
        from reviews.models import Review

        self.stdout.write('Создаю данные...')

        # ── Администратор ──────────────────────────────────────────────
        admin, created = User.objects.get_or_create(
            email='admin@petcare.ru',
            defaults={
                'first_name': 'Админ',
                'last_name': 'Петкеров',
                'role': User.Role.ADMIN,
                'phone': '+7 (495) 100-00-01',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  + Администратор: {admin.email}')

        # ── Специализации ──────────────────────────────────────────────
        specialties_data = [
            ('Терапия', 'Общий осмотр, диагностика и лечение заболеваний внутренних органов'),
            ('Хирургия', 'Оперативные вмешательства любой сложности'),
            ('Офтальмология', 'Диагностика и лечение заболеваний глаз'),
            ('Дерматология', 'Лечение кожных заболеваний, аллергий'),
            ('Стоматология', 'Лечение зубов, ультразвуковая чистка, удаление'),
            ('Кардиология', 'Диагностика и лечение сердечно-сосудистых заболеваний'),
            ('Гастроэнтерология', 'Лечение заболеваний желудочно-кишечного тракта'),
            ('Неврология', 'Диагностика и лечение неврологических нарушений'),
            ('Урология', 'Лечение заболеваний мочеполовой системы'),
            ('Эндокринология', 'Лечение гормональных нарушений и обмена веществ'),
        ]
        specialties = {}
        for name, desc in specialties_data:
            obj, _ = Specialty.objects.get_or_create(name=name, defaults={'description': desc})
            specialties[name] = obj
        self.stdout.write(f'  + Специализации: {len(specialties)}')

        # ── Врачи ──────────────────────────────────────────────────────
        doctors_data = [
            {
                'email': 'ivanov@petcare.ru',
                'first_name': 'Алексей',
                'last_name': 'Иванов',
                'phone': '+7 (495) 200-00-01',
                'experience_years': 15,
                'education': 'МГАВМиБ им. К.И. Скрябина, ветеринарная хирургия, 2009',
                'bio': 'Специализируется на абдоминальной и ортопедической хирургии мелких домашних животных. Провёл более 3000 операций.',
                'consultation_price': Decimal('3500'),
                'primary': 'Хирургия',
                'secondary': ['Терапия'],
            },
            {
                'email': 'petrova@petcare.ru',
                'first_name': 'Елена',
                'last_name': 'Петрова',
                'phone': '+7 (495) 200-00-02',
                'experience_years': 12,
                'education': 'СПбГАВМ, ветеринарная медицина, 2012',
                'bio': 'Терапевт широкого профиля. Ведёт приём кошек и собак. Особый интерес — гастроэнтерология.',
                'consultation_price': Decimal('2500'),
                'primary': 'Терапия',
                'secondary': ['Кардиология'],
            },
            {
                'email': 'sidorov@petcare.ru',
                'first_name': 'Дмитрий',
                'last_name': 'Сидоров',
                'phone': '+7 (495) 200-00-03',
                'experience_years': 8,
                'education': 'КФУ, ветеринария, 2016',
                'bio': 'Ветеринар-офтальмолог. Владеет методиками микрохирургии глаза, лазерной коррекции у животных.',
                'consultation_price': Decimal('4000'),
                'primary': 'Офтальмология',
                'secondary': ['Терапия'],
            },
            {
                'email': 'kuznetsova@petcare.ru',
                'first_name': 'Ольга',
                'last_name': 'Кузнецова',
                'phone': '+7 (495) 200-00-04',
                'experience_years': 6,
                'education': 'РУДН, ветеринарная дерматология, 2018',
                'bio': 'Дерматолог, аллерголог. Работает с хроническими кожными патологиями и пищевыми аллергиями.',
                'consultation_price': Decimal('3000'),
                'primary': 'Дерматология',
                'secondary': [],
            },
            {
                'email': 'morozov@petcare.ru',
                'first_name': 'Андрей',
                'last_name': 'Морозов',
                'phone': '+7 (495) 200-00-05',
                'experience_years': 20,
                'education': 'МГАВМиБ им. К.И. Скрябина, стоматология животных, 2004',
                'bio': 'Стоматолог с двадцатилетним стажем. Проводит санацию полости рта, лечение пародонтоза, протезирование клыков.',
                'consultation_price': Decimal('3500'),
                'primary': 'Стоматология',
                'secondary': ['Хирургия'],
            },
            {
                'email': 'volkova@petcare.ru',
                'first_name': 'Наталья',
                'last_name': 'Волкова',
                'phone': '+7 (495) 200-00-06',
                'experience_years': 3,
                'education': 'МГУПП, ветеринария, 2021',
                'bio': 'Кардиолог. Выполняет ЭКГ, ЭхоКГ, холтеровское мониторирование. Молодой перспективный специалист.',
                'consultation_price': Decimal('5000'),
                'primary': 'Кардиология',
                'secondary': ['Терапия'],
            },
            {
                'email': 'lebedev@petcare.ru',
                'first_name': 'Михаил',
                'last_name': 'Лебедев',
                'phone': '+7 (495) 200-00-07',
                'experience_years': 11,
                'education': 'МГАВМиБ им. К.И. Скрябина, гастроэнтерология, 2013',
                'bio': 'Гастроэнтеролог, эндоскопист. Проводит диагностику и лечение хронических гастритов, панкреатита, пищевых нарушений у мелких животных.',
                'consultation_price': Decimal('3200'),
                'primary': 'Гастроэнтерология',
                'secondary': ['Терапия'],
            },
            {
                'email': 'orlova@petcare.ru',
                'first_name': 'Ирина',
                'last_name': 'Орлова',
                'phone': '+7 (495) 200-00-08',
                'experience_years': 9,
                'education': 'СПбГАВМ, ветеринарная неврология, 2015',
                'bio': 'Невролог. Специализируется на эпилептиформных припадках, грыжах межпозвоночных дисков, реабилитации после травм.',
                'consultation_price': Decimal('4500'),
                'primary': 'Неврология',
                'secondary': ['Терапия'],
            },
            {
                'email': 'fedorov@petcare.ru',
                'first_name': 'Артём',
                'last_name': 'Фёдоров',
                'phone': '+7 (495) 200-00-09',
                'experience_years': 14,
                'education': 'МГАВМиБ, урология животных, 2010',
                'bio': 'Уролог-нефролог. Лечение мочекаменной болезни, цистита, хронической почечной недостаточности. Проведение цистоскопии.',
                'consultation_price': Decimal('3800'),
                'primary': 'Урология',
                'secondary': ['Хирургия'],
            },
            {
                'email': 'belova@petcare.ru',
                'first_name': 'Светлана',
                'last_name': 'Белова',
                'phone': '+7 (495) 200-00-10',
                'experience_years': 7,
                'education': 'РУДН, эндокринология, 2017',
                'bio': 'Эндокринолог. Диагностика сахарного диабета, гипер- и гипотиреоза. Подбор инсулинотерапии.',
                'consultation_price': Decimal('3500'),
                'primary': 'Эндокринология',
                'secondary': [],
            },
        ]

        doctors = []
        for d in doctors_data:
            user, created = User.objects.get_or_create(
                email=d['email'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                    'phone': d['phone'],
                    'role': User.Role.VETERINARIAN,
                },
            )
            if created:
                user.set_password('password123')
                user.save()

            doctor, _ = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'experience_years': d['experience_years'],
                    'education': d['education'],
                    'bio': d['bio'],
                    'consultation_price': d['consultation_price'],
                    'is_available': True,
                },
            )

            DoctorSpecialty.objects.get_or_create(
                doctor=doctor,
                specialty=specialties[d['primary']],
                defaults={'is_primary': True},
            )
            for sec in d['secondary']:
                DoctorSpecialty.objects.get_or_create(
                    doctor=doctor,
                    specialty=specialties[sec],
                    defaults={'is_primary': False},
                )

            for day in range(6):
                Schedule.objects.get_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    defaults={
                        'start_time': time(9, 0),
                        'end_time': time(18, 0),
                    },
                )

            doctors.append(doctor)

        self.stdout.write(f'  + Врачи: {len(doctors)}')

        # ── Услуги ─────────────────────────────────────────────────────
        services_data = [
            ('Первичный приём терапевта', 'Осмотр, сбор анамнеза, назначение обследований', Decimal('2000'), 30, 'Терапия'),
            ('Повторный приём терапевта', 'Контрольный осмотр, коррекция лечения', Decimal('1500'), 20, 'Терапия'),
            ('Вакцинация', 'Комплексная вакцинация с оформлением ветпаспорта', Decimal('2500'), 20, 'Терапия'),
            ('Кастрация кота', 'Плановая операция под общим наркозом', Decimal('4500'), 60, 'Хирургия'),
            ('Стерилизация кошки', 'Лапароскопическая стерилизация', Decimal('7000'), 90, 'Хирургия'),
            ('Удаление новообразования', 'Хирургическое удаление с гистологическим исследованием', Decimal('8500'), 120, 'Хирургия'),
            ('Осмотр офтальмолога', 'Комплексное обследование глаз, тест Ширмера, тонометрия', Decimal('3000'), 40, 'Офтальмология'),
            ('Лечение конъюнктивита', 'Диагностика и назначение терапии при воспалении глаз', Decimal('2500'), 30, 'Офтальмология'),
            ('Приём дерматолога', 'Осмотр кожи, соскобы, люминесцентная диагностика', Decimal('3000'), 40, 'Дерматология'),
            ('Лечение аллергии', 'Подбор элиминационной диеты, назначение терапии', Decimal('3500'), 45, 'Дерматология'),
            ('Ультразвуковая чистка зубов', 'Снятие зубного камня ультразвуком под седацией', Decimal('5000'), 60, 'Стоматология'),
            ('Удаление зуба', 'Экстракция зуба любой сложности', Decimal('3500'), 45, 'Стоматология'),
            ('ЭКГ', 'Электрокардиографическое исследование', Decimal('2000'), 30, 'Кардиология'),
            ('ЭхоКГ', 'Ультразвуковое исследование сердца', Decimal('4500'), 45, 'Кардиология'),
        ]

        services = []
        for name, desc, price, dur, spec_name in services_data:
            svc, _ = Service.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'price': price,
                    'duration_minutes': dur,
                    'specialty': specialties[spec_name],
                    'is_active': True,
                },
            )
            services.append(svc)
        self.stdout.write(f'  + Услуги: {len(services)}')

        # ── Клиенты и питомцы ─────────────────────────────────────────
        clients_data = [
            {
                'email': 'maria@example.com',
                'first_name': 'Мария',
                'last_name': 'Смирнова',
                'phone': '+7 (916) 111-22-33',
                'pets': [
                    ('Барсик', 'cat', 'Британская короткошёрстная', 36, Decimal('5.20'), 'Склонность к мочекаменной болезни'),
                    ('Рекс', 'dog', 'Немецкая овчарка', 60, Decimal('34.00'), 'Дисплазия тазобедренного сустава'),
                    ('Чирик', 'bird', 'Волнистый попугай', 18, Decimal('0.04'), ''),
                ],
            },
            {
                'email': 'sergey@example.com',
                'first_name': 'Сергей',
                'last_name': 'Козлов',
                'phone': '+7 (926) 444-55-66',
                'pets': [
                    ('Мурка', 'cat', 'Сибирская', 24, Decimal('4.10'), 'Аллергия на курицу'),
                    ('Тузик', 'dog', 'Лабрадор-ретривер', 48, Decimal('28.50'), ''),
                    ('Шустрик', 'rodent', 'Хомяк джунгарик', 6, Decimal('0.05'), ''),
                ],
            },
            {
                'email': 'anna@example.com',
                'first_name': 'Анна',
                'last_name': 'Лебедева',
                'phone': '+7 (916) 222-33-44',
                'pets': [
                    ('Феликс', 'cat', 'Мейн-кун', 30, Decimal('7.50'), 'Гипертрофическая кардиомиопатия — наблюдение'),
                    ('Граф', 'dog', 'Корги', 24, Decimal('11.00'), ''),
                ],
            },
            {
                'email': 'pavel@example.com',
                'first_name': 'Павел',
                'last_name': 'Новиков',
                'phone': '+7 (916) 333-44-55',
                'pets': [
                    ('Маркиз', 'cat', 'Шотландская вислоухая', 48, Decimal('5.80'), ''),
                ],
            },
            {
                'email': 'ekaterina@example.com',
                'first_name': 'Екатерина',
                'last_name': 'Соколова',
                'phone': '+7 (916) 444-55-66',
                'pets': [
                    ('Локки', 'dog', 'Хаски', 36, Decimal('22.00'), 'Дисплазия локтевого сустава'),
                ],
            },
            {
                'email': 'vladimir@example.com',
                'first_name': 'Владимир',
                'last_name': 'Морозов',
                'phone': '+7 (916) 555-66-77',
                'pets': [
                    ('Зефир', 'rodent', 'Морская свинка', 12, Decimal('1.10'), ''),
                ],
            },
            {
                'email': 'olga@example.com',
                'first_name': 'Ольга',
                'last_name': 'Петрова',
                'phone': '+7 (916) 666-77-88',
                'pets': [],
            },
            {
                'email': 'igor@example.com',
                'first_name': 'Игорь',
                'last_name': 'Васильев',
                'phone': '+7 (916) 777-88-99',
                'pets': [],
            },
            {
                'email': 'tatiana@example.com',
                'first_name': 'Татьяна',
                'last_name': 'Зайцева',
                'phone': '+7 (916) 888-99-00',
                'pets': [],
            },
            {
                'email': 'roman@example.com',
                'first_name': 'Роман',
                'last_name': 'Волков',
                'phone': '+7 (916) 999-00-11',
                'pets': [],
            },
        ]

        clients = []
        pets = []
        for c in clients_data:
            user, created = User.objects.get_or_create(
                email=c['email'],
                defaults={
                    'first_name': c['first_name'],
                    'last_name': c['last_name'],
                    'phone': c['phone'],
                    'role': User.Role.CLIENT,
                },
            )
            if created:
                user.set_password('password123')
                user.save()
            clients.append(user)

            for pname, species, breed, age, weight, notes in c['pets']:
                pet, _ = Pet.objects.get_or_create(
                    owner=user,
                    name=pname,
                    defaults={
                        'species': species,
                        'breed': breed,
                        'age': age,
                        'weight': weight,
                        'health_notes': notes,
                    },
                )
                pets.append(pet)

        self.stdout.write(f'  + Клиенты: {len(clients)}, Питомцы: {len(pets)}')

        # ── Записи на приём ────────────────────────────────────────────
        today = date.today()

        appointments_data = [
            # completed (прошедшие)
            (clients[0], doctors[1], pets[0], services[0], today - timedelta(days=30), time(10, 0), 'completed', 'Первичный осмотр, жалобы на аппетит'),
            (clients[0], doctors[0], pets[1], services[3], today - timedelta(days=25), time(11, 0), 'completed', 'Плановая кастрация'),
            (clients[1], doctors[1], pets[3], services[2], today - timedelta(days=20), time(9, 30), 'completed', 'Ежегодная вакцинация'),
            (clients[1], doctors[2], pets[4], services[7], today - timedelta(days=18), time(14, 0), 'completed', 'Слезотечение из левого глаза'),
            (clients[0], doctors[3], pets[0], services[8], today - timedelta(days=15), time(12, 0), 'completed', 'Зуд, расчёсы на холке'),
            (clients[1], doctors[4], pets[4], services[10], today - timedelta(days=10), time(10, 30), 'completed', 'Плановая чистка зубов'),
            (clients[0], doctors[5], pets[1], services[12], today - timedelta(days=7), time(15, 0), 'completed', 'Контроль ЭКГ после нагрузки'),
            (clients[2], doctors[6], pets[6], services[0], today - timedelta(days=40), time(11, 0), 'completed', 'Жалобы на рвоту по утрам'),
            (clients[3], doctors[7], pets[8], services[0], today - timedelta(days=35), time(13, 30), 'completed', 'Эпизоды судорог'),
            (clients[2], doctors[8], pets[7], services[0], today - timedelta(days=22), time(15, 30), 'completed', 'Учащённое мочеиспускание'),
            # confirmed (ближайшие)
            (clients[0], doctors[1], pets[0], services[1], today + timedelta(days=1), time(10, 0), 'confirmed', 'Повторный приём после лечения'),
            (clients[1], doctors[3], pets[3], services[9], today + timedelta(days=2), time(11, 30), 'confirmed', 'Контроль аллергии, подбор диеты'),
            # pending
            (clients[1], doctors[5], pets[4], services[13], today + timedelta(days=5), time(14, 0), 'pending', ''),
            (clients[0], doctors[0], pets[1], services[5], today + timedelta(days=7), time(9, 0), 'pending', 'Липома на боку, нужно удалить'),
            # cancelled
            (clients[0], doctors[2], pets[0], services[6], today - timedelta(days=3), time(16, 0), 'cancelled', 'Осмотр глаз'),
            (clients[1], doctors[1], pets[4], services[0], today - timedelta(days=5), time(13, 0), 'cancelled', ''),
        ]

        appointments = []
        for client, doctor, pet, service, d, t, status, comment in appointments_data:
            apt, _ = Appointment.objects.get_or_create(
                client=client,
                doctor=doctor,
                pet=pet,
                service=service,
                date=d,
                time_slot=t,
                defaults={
                    'status': status,
                    'comment': comment,
                    'cancel_reason': 'Клиент не смог приехать' if status == 'cancelled' else '',
                },
            )
            appointments.append(apt)

        self.stdout.write(f'  + Записи: {len(appointments)}')

        # ── Отзывы ─────────────────────────────────────────────────────
        completed = [a for a in appointments if a.status == 'completed']

        reviews_data = [
            (completed[0], 5, 'Елена Васильевна — замечательный терапевт. Внимательно осмотрела Барсика, всё подробно объяснила. Назначила анализы, через неделю аппетит восстановился.', True),
            (completed[1], 5, 'Операция прошла отлично, Рекс быстро восстановился. Алексей Иванов — хирург от бога. Рекомендую!', True),
            (completed[2], 4, 'Хороший приём, вакцинацию сделали быстро. Единственное — пришлось подождать 15 минут в очереди.', True),
            (completed[3], 5, 'Дмитрий Сидоров очень аккуратно осмотрел глаза Тузику, назначил капли. Через неделю слезотечение полностью прошло.', True),
            (completed[4], 3, 'Врач компетентный, но приём показался слишком коротким. Хотелось бы более детальных объяснений по уходу за кожей.', False),
            (completed[5], 4, 'Чистку зубов провели профессионально. Тузик перенёс седацию хорошо, зубы как новые.', True),
            (completed[6], 5, 'Наталья Волкова провела ЭКГ, всё подробно расшифровала. Сердце Рекса в порядке, очень рады!', False),
            (completed[7], 5, 'Михаил Лебедев — внимательный гастроэнтеролог. Подобрали диету, рвота прошла за две недели.', True),
            (completed[8], 5, 'Ирина Орлова провела детальный неврологический осмотр, объяснила результаты МРТ. Очень благодарна.', True),
            (completed[9], 4, 'Артём Фёдоров — грамотный специалист. УЗИ почек прошло хорошо, диагноз подтвердился.', True),
        ]

        review_count = 0
        for apt, rating, text, approved in reviews_data:
            _, created = Review.objects.get_or_create(
                appointment=apt,
                defaults={
                    'author': apt.client,
                    'doctor': apt.doctor,
                    'rating': rating,
                    'text': text,
                    'is_approved': approved,
                },
            )
            if created:
                review_count += 1

        self.stdout.write(f'  + Отзывы: {review_count}')

        # ── Медкарты (для completed-приёмов) ─────────────────────────
        medical_records_data = [
            (completed[0], 'Гастрит лёгкой степени', 'Диетический корм, Смекта 2 раза в день 5 дней', 'Повторный приём через 10 дней'),
            (completed[1], 'Состояние после кастрации', 'Обработка шва хлоргексидином 2 р/д, 7 дней', 'Носить воротник 10 дней, снять швы через неделю'),
            (completed[2], 'Плановая вакцинация выполнена', 'Вакцина Нобивак DHPPi + RL', 'Следующая вакцинация через 12 месяцев'),
            (completed[3], 'Конъюнктивит (катаральный)', 'Капли Ципровет 3 р/д, 7 дней', 'Контрольный осмотр через неделю'),
            (completed[4], 'Атопический дерматит', 'Апоквел 1 таб/д, шампунь Дуксо', 'Элиминационная диета, повторно через 3 недели'),
            (completed[5], 'Санация полости рта проведена', 'Ультразвуковая чистка, полировка', 'Чистка зубов раз в 6-12 мес.'),
            (completed[6], 'Синусовая тахикардия, ЭКГ без патологий', 'Наблюдение', 'Контрольное ЭКГ через 6 месяцев'),
            (completed[7], 'Хронический гастрит', 'Гастропротектор Омез 1 капс/д, лечебный корм Hill\'s i/d', 'Контроль через 3 недели'),
            (completed[8], 'Идиопатическая эпилепсия', 'Фенобарбитал 2.5 мг/кг 2 р/д', 'Контроль уровня препарата в крови через 2 недели'),
            (completed[9], 'Цистит лёгкой степени', 'Стоп-цистит, обильное питьё, 7 дней', 'Контрольный анализ мочи через 10 дней'),
        ]

        mr_count = 0
        for apt, diagnosis, treatment, recommendations in medical_records_data:
            _, created = MedicalRecord.objects.get_or_create(
                appointment=apt,
                defaults={
                    'pet': apt.pet,
                    'doctor': apt.doctor,
                    'date': apt.date,
                    'diagnosis': diagnosis,
                    'treatment': treatment,
                    'recommendations': recommendations,
                },
            )
            if created:
                mr_count += 1

        self.stdout.write(f'  + Медкарты: {mr_count}')

        self.stdout.write(self.style.SUCCESS('Готово!'))
