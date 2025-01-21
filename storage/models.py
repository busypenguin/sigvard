from django.db import models


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
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена", default=0
    )
    is_occupied = models.BooleanField(verbose_name="Занята", default=False)

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"

    def __str__(self):
        return f"{self.storage.city}, №{self.number}"
