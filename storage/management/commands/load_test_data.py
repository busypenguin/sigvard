from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from storage.models import Storage


class Command(BaseCommand):
    help = "Заполнить базу данных тестовыми данными"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Создание складов
            with open("./static/img/image11.png", "rb") as f:
                storage_1 = Storage.objects.get_or_create(
                    city="Москва",
                    address="ул. Рокотова, д. 15",
                    temperature=17.5,
                    photo=File(f),
                )
            with open("./static/img/image9.png", "rb") as f:
                storage_2 = Storage.objects.get_or_create(
                    city="Одинцово",
                    address="ул. Серверная, д. 36",
                    temperature=18,
                    photo=File(f),
                )
            with open("./static/img/image15.png", "rb") as f:
                storage_3 = Storage.objects.get_or_create(
                    city="Пушкино",
                    address="ул. Строителей, д. 5",
                    temperature=20,
                    photo=File(f),
                )
            with open("./static/img/image16.png", "rb") as f:
                storage_4 = Storage.objects.get_or_create(
                    city="Люберцы",
                    address="ул. Советская, д. 88",
                    temperature=18,
                    photo=File(f),
                )
            with open("./static/img/image151.png", "rb") as f:
                storage_5 = Storage.objects.get_or_create(
                    city="Домодедово",
                    address="ул. Орджоникидзе, д. 29",
                    temperature=21,
                    photo=File(f),
                )

        self.stdout.write(self.style.SUCCESS("Тестовые данные загружены"))
