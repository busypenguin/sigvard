from django.contrib import admin

from .models import Storage, Box, Rent


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    pass


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    pass


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    pass
