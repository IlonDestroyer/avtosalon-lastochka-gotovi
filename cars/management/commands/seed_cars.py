from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from cars.models import Car, Profile


SAMPLE = [
    {
        "brand": "BMW",
        "model": "X5",
        "trim": "xDrive40i",
        "year": 2023,
        "body": "Кроссовер",
        "mileage_km": 18500,
        "fuel": "Бензин",
        "horsepower": 340,
        "transmission": "Автомат",
        "price_kzt": 42500000,
        "description": "Премиальный кроссовер в отличном состоянии, полный привод, панорамная крыша.",
        "image_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
    },
    {
        "brand": "Audi",
        "model": "Q7",
        "trim": "45 TFSI",
        "year": 2022,
        "body": "Кроссовер",
        "mileage_km": 32000,
        "fuel": "Бензин",
        "horsepower": 249,
        "transmission": "Автомат",
        "price_kzt": 38900000,
        "description": "Семиместный кроссовер с богатой комплектацией и адаптивной подвеской.",
        "image_url": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
    },
    {
        "brand": "Mercedes-Benz",
        "model": "E 200",
        "trim": "AMG Line",
        "year": 2024,
        "body": "Седан",
        "mileage_km": 5200,
        "fuel": "Бензин",
        "horsepower": 197,
        "transmission": "Автомат",
        "price_kzt": 35200000,
        "description": "Бизнес-седан AMG Line, почти новый, полный пакет ассистентов.",
        "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800",
    },
    {
        "brand": "Toyota",
        "model": "Camry",
        "trim": "Prestige",
        "year": 2023,
        "body": "Седан",
        "mileage_km": 21000,
        "fuel": "Бензин",
        "horsepower": 181,
        "transmission": "Автомат",
        "price_kzt": 18500000,
        "description": "Надёжный седан в максимальной комплектации Prestige.",
        "image_url": "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=800",
    },
    {
        "brand": "Kia",
        "model": "K5",
        "trim": "GT-Line",
        "year": 2023,
        "body": "Седан",
        "mileage_km": 15000,
        "fuel": "Бензин",
        "horsepower": 180,
        "transmission": "Автомат",
        "price_kzt": 14200000,
        "description": "Стильный седан GT-Line с спортивным характером.",
        "image_url": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?w=800",
    },
    {
        "brand": "Hyundai",
        "model": "Tucson",
        "trim": "Prestige",
        "year": 2022,
        "body": "Кроссовер",
        "mileage_km": 28000,
        "fuel": "Бензин",
        "horsepower": 150,
        "transmission": "Автомат",
        "price_kzt": 16800000,
        "description": "Популярный кроссовер в комплектации Prestige, полный привод.",
        "image_url": "https://images.unsplash.com/photo-1616422285623-13ea554d3c71?w=800",
    },
]


class Command(BaseCommand):
    help = "Заполняет каталог демо-автомобилями и создаёт суперпользователя admin/admin"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            user = User.objects.create_superuser("admin", "admin@lastocka.kz", "admin")
            Profile.objects.update_or_create(
                user=user,
                defaults={"full_name": "Администратор", "phone": "+77000000000"},
            )
            self.stdout.write(self.style.SUCCESS("Создан суперпользователь admin / admin"))
        else:
            self.stdout.write("Суперпользователь admin уже существует")

        created = 0
        for item in SAMPLE:
            if not Car.objects.filter(brand=item["brand"], model=item["model"], trim=item["trim"]).exists():
                Car.objects.create(**item)
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Добавлено автомобилей: {created}"))
