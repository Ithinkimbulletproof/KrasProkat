from django import forms
from .models import InventoryItem, RentalOrder, Customer
from django.core.exceptions import ValidationError

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            "name",
            "description",
            "category",
            "price_per_day",
            "available_quantity",
            "image",
        ]
        labels = {
            "name": "Название",
            "description": "Описание",
            "category": "Категория",
            "price_per_day": "Цена за день",
            "available_quantity": "Доступное количество",
            "image": "Изображение",
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        labels = {
            "name": "Имя",
            "phone": "Телефон",
            "email": "Email",
            "address": "Адрес",
        }

class RentalOrderForm(forms.ModelForm):
    class Meta:
        model = RentalOrder
        fields = [
            "item",
            "customer",
            "rental_start_date",
            "rental_end_date",
            "is_active",
        ]
        labels = {
            "item": "Товар",
            "customer": "Клиент",
            "rental_start_date": "Дата начала аренды",
            "rental_end_date": "Дата окончания аренды",
            "total_price": "Итоговая цена",
            "is_active": "Активный",
        }

    def clean(self):
        cleaned_data = super().clean()
        rental_start_date = cleaned_data.get("rental_start_date")
        rental_end_date = cleaned_data.get("rental_end_date")

        if rental_start_date and rental_end_date:
            if rental_start_date >= rental_end_date:
                raise ValidationError("Дата окончания аренды должна быть позже даты начала.")
