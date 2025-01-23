from django.contrib import admin

from .models import Storage, Box, Rent


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    pass


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    search_fields = ("box",)


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    readonly_fields = ("total_price", "task_ids")
    raw_id_fields = ("user", "box")
    autocomplete_fields = ["user", "box"]
    list_filter = ["status"]
