from django import forms
from django.core.exceptions import ValidationError
from .models import InventoryItem, InventoryStock, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        labels = {
            "name": "Название категории",
            "description": "Описание категории",
        }
        error_messages = {
            "name": {
                "required": "Это поле обязательно для заполнения.",
                "unique": "Категория с таким названием уже существует.",
            },
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["name", "description", "category", "price_per_day", "image"]
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
        fields = ["location", "total_quantity", "available_quantity"]
        labels = {
            "location": "Местоположение (магазин)",
            "total_quantity": "Общее количество",
            "available_quantity": "Доступное количество",
        }
        help_texts = {
            "total_quantity": "Введите общее количество инструмента, доступного в магазине.",
            "available_quantity": "Введите количество доступных единиц товара.",
        }

    def clean_total_quantity(self):
        total_quantity = self.cleaned_data.get("total_quantity")
        if total_quantity < 0:
            raise ValidationError("Общее количество не может быть отрицательным.")
        return total_quantity

    def clean_available_quantity(self):
        available_quantity = self.cleaned_data.get("available_quantity")
        if available_quantity < 0:
            raise ValidationError("Доступное количество не может быть отрицательным.")
        return available_quantity
