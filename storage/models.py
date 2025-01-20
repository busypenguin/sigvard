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
