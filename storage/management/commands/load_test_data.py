import random

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from storage.models import Storage, Box


class Command(BaseCommand):
    help = "Заполнить базу данных тестовыми данными"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Создание складов
            with open("./static/img/image11.png", "rb") as f:
                storage_1, created = Storage.objects.get_or_create(
                    city="Москва",
                    address="ул. Рокотова, д. 15",
                    temperature=17.5,
                    photo=File(f),
                )
            with open("./static/img/image9.png", "rb") as f:
                storage_2, created = Storage.objects.get_or_create(
                    city="Одинцово",
                    address="ул. Серверная, д. 36",
                    temperature=18,
                    photo=File(f),
                )
            with open("./static/img/image15.png", "rb") as f:
                storage_3, created = Storage.objects.get_or_create(
                    city="Пушкино",
                    address="ул. Строителей, д. 5",
                    temperature=20,
                    photo=File(f),
                )
            with open("./static/img/image16.png", "rb") as f:
                storage_4, created = Storage.objects.get_or_create(
                    city="Люберцы",
                    address="ул. Советская, д. 88",
                    temperature=18,
                    photo=File(f),
                )
            with open("./static/img/image151.png", "rb") as f:
                storage_5, created = Storage.objects.get_or_create(
                    city="Домодедово",
                    address="ул. Орджоникидзе, д. 29",
                    temperature=21,
                    photo=File(f),
                )
            storages = [storage_1, storage_2, storage_3, storage_4, storage_5]
            # Создание боксов
            for num, stor in enumerate(storages):
                for i in range(10):
                    level = random.randint(1, 4)
                    number = f"{num}{random.randint(100, 999)}-{level}{i}"
                    height = round(random.uniform(2.0, 4.0), 1)
                    width = round(random.uniform(2.0, 5.0), 1)
                    length = round(random.uniform(1.0, 4.0), 1)
                    price = random.randint(1000, 5000)
                    Box.objects.create(
                        number=number,
                        storage=stor,
                        level=level,
                        height=height,
                        width=width,
                        length=length,
                        price=price,
                    )

        self.stdout.write(self.style.SUCCESS("Тестовые данные загружены"))
