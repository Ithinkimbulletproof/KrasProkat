from django.contrib import admin
from .models import (InventoryItem, InventoryStock, RentalOrder, RentalLocation, Profile, NewsItem, CarouselImage)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_per_day")
    search_fields = ("name", "category")
    list_filter = ("category",)
    ordering = ("name",)

@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = ("item", "location", "total_quantity", "available_quantity")
    list_filter = ("location", "item")
    search_fields = ("item__name", "location__name")
    ordering = ("item",)

@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    list_display = ("item", "customer", "location", "rental_start_date", "rental_end_date", "total_price", "is_active")
    search_fields = ("item__name", "customer__first_name", "customer__last_name", "location__name")
    list_filter = ("location", "is_active")
    date_hierarchy = "rental_start_date"
    ordering = ("-rental_start_date",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "first_name", "last_name", "phone", "email")
    list_filter = ("role",)
    search_fields = ("user__username", "first_name", "last_name")
    ordering = ("user",)

@admin.register(RentalLocation)
class RentalLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone")
    search_fields = ("name", "address")
    ordering = ("name",)

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    ordering = ['order']

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'category']
    list_filter = ['category', 'date']
