from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

import storage.messages as msg
from sigvard.celery import app
from .tasks import (
    send_email_message_task,
    send_monthly_email_reminder,
    set_rent_status_to_expired_task,
)


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
        max_digits=10, decimal_places=2, verbose_name="Цена за месяц", default=0
    )
    is_occupied = models.BooleanField(verbose_name="Занята", default=False)

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"

    def __str__(self):
        return f"{self.storage.city}, №{self.number}"

    def save(self, *args, **kwargs):
        self.area = self.width * self.length
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
    task_ids = models.JSONField(default=list, verbose_name="ID задач напоминаний")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            # Действия, выполняемые при создании записи
            super().save(*args, **kwargs)
            self.send_confirm_rent_message()
            self.set_rent_status_to_expired()
            self.schedule_rent_reminders()
        else:
            # Действия, выполняемые при обновлении записи
            self.handle_status_changes()

        self.set_delivery_flag()
        self.calculate_rental_price()
        self.link_user_by_email()

        super().save(*args, **kwargs)

    # Вспомогательные методы

    def set_delivery_flag(self):
        """Устанавливает флаг необходимости доставки, если указан адрес забора груза"""
        self.is_delivery_needed = True if self.pickup_address else False

    def calculate_rental_price(self):
        """Рассчитывает стоимость аренды, если заданы даты"""
        if self.start_date and self.end_date:
            rental_days = (self.end_date - self.start_date).days + 1
            daily_price = self.box.price / 30
            self.total_price = rental_days * daily_price

    def link_user_by_email(self):
        """Связывает аренду с пользователем, если указан email"""
        if self.email and not self.user:
            try:
                self.user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                pass  # Пользователь не найден, оставляем поле user пустым

    def send_confirm_rent_message(self):
        """Отправляет письмо подтверждение создания заказа аренды"""
        subject, message = msg.create_confirm_rent_message(self)
        send_email_message_task.delay(subject, message, self.email)

    def set_rent_status_to_expired(self):
        """Запланировать задачу изменить статус на 'просрочено' в конце срока аренды"""
        task = set_rent_status_to_expired_task.apply_async(
            (self.pk,),
            countdown=(self.end_date - now()).total_seconds(),
        )
        self.task_ids.append(task.id)

    def schedule_rent_reminders(self) -> list:
        """Запланировать задачи для периодических напоминаний об окончании аренды."""
        delays = {30: "месяц", 14: "2 недели", 7: "неделю", 3: "3 дня"}
        for delay, time_insert in delays.items():
            countdown = (self.end_date - timedelta(days=delay) - now()).total_seconds()
            if countdown > 0:
                subject, message = msg.create_notif_end_rent_message(self, time_insert)
                task = send_email_message_task.apply_async(
                    (subject, message, self.email), countdown=countdown
                )
                self.task_ids.append(task.id)

    def handle_status_changes(self):
        """Обрабатывает изменения статуса аренды"""
        old_status = Rent.objects.get(pk=self.pk).status
        new_status = self.status

        # Если статус изменился
        if old_status != new_status:
            if new_status in ["completed", "cancelled"]:
                self.remove_related_tasks()
            elif new_status == "expired":
                self.schedule_reminder_for_overdue_rent()

    def remove_related_tasks(self):
        """Удаляет связанные задачи, если аренда завершена или отменена"""
        for task_id in self.task_ids:
            app.control.revoke(task_id, terminate=True)
        self.task_ids = []

    def schedule_reminder_for_overdue_rent(self):
        """Запланировать напоминание об просроченной аренде"""
        subject, message = msg.create_reminder_for_overdue_rent_message(self)
        send_monthly_email_reminder.delay(self.pk, subject, message)

    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"

    def __str__(self):
        return f"Аренда бокса {self.box.number} пользователем {self.email}"
