import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from vehicles.models import Vehicle
from orders.models import Order, TripAssignment, DriverProfile
from routes.models import Route

fake = Faker('ru_RU')  # Генерируем данные на русском языке
User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет базу данных фейковыми пользователями, машинами и заказами"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== Старт заполнения БД ==="))

        # 1. Создаем диспетчера (если еще нет)
        dispatcher, created = User.objects.get_or_create(
            username="dispatcher_seed",
            defaults={
                "first_name": "Иван",
                "email": fake.unique.email(),
                "phone": "+79991112233",
                "role": "dispatcher",
                "is_active": True
            }
        )
        if created:
            dispatcher.set_password("password123")
            dispatcher.save()

        # 2. Создаем Клиентов
        clients = []
        for _ in range(5):
            username = fake.user_name() + str(random.randint(10, 99))
            client = User(
                username=username,
                first_name=fake.first_name(),
                email=fake.unique.email(),  # Уникальный email для клиента
                phone=fake.phone_number().replace(" ", "").replace("-", "")[:12],
                role="client",
                is_active=True
            )
            client.set_password("password123")
            client.save()
            clients.append(client)
        self.stdout.write(self.style.SUCCESS(f"Создано клиентов: {len(clients)}"))

        # 3. Создаем Водителей и Транспорт
        marks = ["Камаз Нео", "Scania R450", "Volvo FH16", "MAN TGX", "Газель Next", "Mercedes Actros"]

        for i in range(5):
            username = f"driver_{fake.user_name()}{random.randint(10, 99)}"
            driver = User(
                username=username,
                first_name=fake.first_name_male(),
                email=fake.unique.email(),  # Уникальный email для водителя
                phone=fake.phone_number().replace(" ", "").replace("-", "")[:12],
                role="driver",
                is_active=True
            )
            driver.set_password("password123")
            driver.save()

            # Проверяем профиль
            driver_profile, _ = DriverProfile.objects.get_or_create(user=driver)

            # Госномер А123БВ777
            plate = f"{random.choice('АВЕКМНОРСТУХ')}{random.randint(100, 999)}{random.choice('АВЕКМНОРСТУХ')}{random.choice('АВЕКМНОРСТУХ')}{random.randint(77, 799)}"

            # Привязываем водителя к машине
            Vehicle.objects.create(
                mark=random.choice(marks),
                plate_number=plate,
                capacity=round(random.uniform(1.5, 20.0), 1),  # Округление до 1 знака
                base_rate_per_km=random.randint(40, 120),
                mileage=random.randint(10000, 300000),
                driver=driver,
                is_active=True
            )
        self.stdout.write(self.style.SUCCESS("Созданы водители и автопарк."))

        # 4. Создаем Заказы
        cities = ["Москва", "Санкт-Петербург", "Краснодар", "Нижний Новгород", "Казань", "Ростов-на-Дону",
                  "Екатеринбург"]

        for _ in range(8):
            load_city = random.choice(cities)
            unload_city = random.choice([c for c in cities if c != load_city])

            loading = f"г. {load_city}, {fake.street_address()}"
            unloading = f"г. {unload_city}, {fake.street_address()}"

            route_obj, _ = Route.objects.get_or_create(
                loading_address=loading,
                unloading_address=unloading,
                defaults={"distance_km": random.randint(150, 1200)}
            )

            order = Order.objects.create(
                client=random.choice(clients),
                loading_address=loading,
                unloading_address=unloading,
                weight=round(random.uniform(0.5, 15.0), 1),
                volume=round(random.uniform(5.0, 80.0), 1),
                description=fake.sentence(nb_words=5),
                status="created",
                route=route_obj
            )

            if hasattr(order, 'calculate_price'):
                order.calculate_price()
                order.save()

        self.stdout.write(self.style.SUCCESS("База данных успешно наполнена фейковыми заказами!"))