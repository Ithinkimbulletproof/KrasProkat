from django import forms
from django.core.exceptions import ValidationError
from .models import InventoryItem, InventoryStock, RentalOrder, Customer, RentalLocation


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            "name",
            "description",
            "category",
            "price_per_day",
            "image",
        ]
        labels = {
            "name": "Название",
            "description": "Описание",
            "category": "Категория",
            "price_per_day": "Цена за день",
            "image": "Изображение",
        }


class InventoryStockForm(forms.ModelForm):
    class Meta:
        model = InventoryStock
        fields = ["location", "total_quantity"]
        labels = {
            "location": "Местоположение (магазин)",
            "total_quantity": "Общее количество",
        }
        help_texts = {
            "total_quantity": "Введите общее количество инструмента, доступного в магазине."
        }

    def clean_total_quantity(self):
        total_quantity = self.cleaned_data.get("total_quantity")
        if total_quantity < 0:
            raise ValidationError("Общее количество не может быть отрицательным.")
        return total_quantity


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
    location = forms.ModelChoiceField(
        queryset=RentalLocation.objects.all(),
        label="Магазин",
        required=True,
        help_text="Выберите магазин, из которого будет взят товар.",
    )

    class Meta:
        model = RentalOrder
        fields = [
            "item",
            "customer",
            "location",
            "rental_start_date",
            "rental_end_date",
            "is_active",
        ]
        labels = {
            "item": "Товар",
            "customer": "Клиент",
            "rental_start_date": "Дата начала аренды",
            "rental_end_date": "Дата окончания аренды",
            "is_active": "Активный",
        }

    def clean(self):
        cleaned_data = super().clean()
        rental_start_date = cleaned_data.get("rental_start_date")
        rental_end_date = cleaned_data.get("rental_end_date")
        item = cleaned_data.get("item")
        location = cleaned_data.get("location")

        if rental_start_date and rental_end_date:
            if rental_start_date >= rental_end_date:
                raise ValidationError(
                    "Дата окончания аренды должна быть позже даты начала."
                )

        if item and location:
            stock = InventoryStock.objects.filter(item=item, location=location).first()
            if stock and stock.available_quantity <= 0:
                raise ValidationError("Недостаточно доступного количества товара в выбранном магазине.")
        return cleaned_data
