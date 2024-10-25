from django.contrib import admin
from .models import InventoryItem, Customer, RentalOrder, RentalLocation

admin.site.register(InventoryItem)
admin.site.register(Customer)
admin.site.register(RentalOrder)
admin.site.register(RentalLocation)
