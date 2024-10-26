from django.contrib import admin
from .models import InventoryItem, Customer, RentalOrder, RentalLocation

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_day', 'available_quantity')
    search_fields = ('name', 'category')

admin.site.register(Customer)
admin.site.register(RentalOrder)
admin.site.register(RentalLocation)
