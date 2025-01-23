from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Storage(models.Model):
    photo = models.ImageField(upload_to="storage_images/", verbose_name="Фото")
    city = models.CharField(max_length=255, verbose_name="Город")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    temperature = models.FloatField(verbose_name="Температура")
    contact = models.CharField(max_length=255, verbose_name="Контакты", blank=True)
    description = models.CharField(max_length=1024, verbose_name="Описание", blank=True)
    directions = models.CharField(max_length=255, verbose_name="Проезд", blank=True)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return f"{self.city}, {self.address}"


class Box(models.Model):
    number = models.CharField(
        max_length=255, verbose_name="Номер бокса", unique=True, db_index=True
    )
    storage = models.ForeignKey(
        Storage, on_delete=models.CASCADE, verbose_name="Склад", related_name="boxes"
    )
    level = models.IntegerField(verbose_name="Этаж")
    height = models.FloatField(verbose_name="Высота, м.")
    width = models.FloatField(verbose_name="Ширина, м.")
    length = models.FloatField(verbose_name="Длина, м.")
    area = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name="Площадь, м²", default=0
        )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена", default=0
    )
    is_occupied = models.BooleanField(verbose_name="Занята", default=False)

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"

    def __str__(self):
        return f"{self.storage.city}, №{self.number}"

    def save(self, *args, **kwargs):
        self.area = self.width + self.length
        super().save(*args, **kwargs)


class Rent(models.Model):
    RENT_STATUS_CHOICES = (
        ("created", "Создана"),
        ("active", "Активна"),
        ("completed", "Завершена"),
        ("cancelled", "Отменена"),
        ("expired", "Просрочена"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rents",
        verbose_name="Арендатор",
        null=True,
        blank=True,
    )
    email = models.EmailField(verbose_name="Email клиента", null=True, blank=True)
    box = models.ForeignKey(
        Box,
        on_delete=models.PROTECT,
        related_name="rents",
        verbose_name="Арендуемый бокс",
    )
    start_date = models.DateTimeField(default=now, verbose_name="Дата начала аренды")
    end_date = models.DateTimeField(verbose_name="Дата окончания аренды")
    status = models.CharField(
        max_length=20,
        choices=RENT_STATUS_CHOICES,
        default="created",
        verbose_name="Статус аренды",
    )
    pickup_address = models.CharField(
        max_length=255, verbose_name="Адрес забора груза", blank=True, null=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Общая сумма аренды", default=0
    )
    is_delivery_needed = models.BooleanField(verbose_name="Нужна доставка")
    is_partial_pickup_allowed = models.BooleanField(
        default=False, verbose_name="Можно забирать частично"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        # Если адрес указан, автоматически ставим флаг необходимости доставки
        self.is_delivery_needed = True if self.pickup_address else False

        # Расчет стоимости аренды
        if self.start_date and self.end_date:
            rental_days = (self.end_date - self.start_date).days + 1
            daily_price = self.box.price
            self.total_price = rental_days * daily_price

        # Если email указан, пробуем найти пользователя
        if self.email and not self.user:
            try:
                self.user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                pass  # Пользователь не найден, оставляем поле user пустым

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"

    def __str__(self):
        return f"Аренда бокса {self.box.number} пользователем {self.email}"
