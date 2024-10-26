from django.contrib import admin
from .models import InventoryItem, Customer, RentalOrder, RentalLocation, InventoryStock


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_per_day")
    search_fields = ("name", "category")


@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = ("item", "location", "total_quantity", "available_quantity")
    list_filter = ("location",)
    search_fields = ("item__name",)

    def available_quantity(self, obj):
        return obj.total_quantity - obj.rented_quantity

    available_quantity.short_description = "Доступное количество"


@admin.register(RentalLocation)
class RentalLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone")
    search_fields = ("name", "address")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")


@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "customer",
        "location",
        "rental_start_date",
        "rental_end_date",
        "is_active",
    )
    list_filter = ("is_active", "location")
    search_fields = ("item__name", "customer__name")
    date_hierarchy = "rental_start_date"
