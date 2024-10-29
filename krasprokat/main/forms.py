from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import InventoryItem, InventoryStock, RentalOrder, Customer, RentalLocation, Profile

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
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
        fields = ["item", "customer", "location", "rental_start_date", "rental_end_date", "is_active"]
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
                raise ValidationError("Дата окончания аренды должна быть позже даты начала.")

        if item and location:
            stock = InventoryStock.objects.filter(item=item, location=location).first()
            if stock and stock.available_quantity <= 0:
                raise ValidationError("Недостаточно доступного количества товара в выбранном магазине.")
        return cleaned_data

class SellerCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        labels = {
            "username": "Имя пользователя",
            "password": "Пароль",
        }
        widgets = {
            "password": forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role"]
        labels = {"role": "Роль"}
