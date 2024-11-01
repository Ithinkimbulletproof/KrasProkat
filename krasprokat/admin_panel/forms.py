from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from inventory.models import InventoryStock
from .models import RentalOrder, RentalLocation


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

class LocationForm(forms.ModelForm):
    class Meta:
        model = RentalLocation
        fields = ['name', 'address', 'phone']

class RentalLocationForm(forms.ModelForm):
    class Meta:
        model = RentalLocation
        fields = ['name', 'address', 'phone']
        labels = {
            'name': 'Название магазина',
            'address': 'Адрес',
            'phone': 'Телефон',
        }
