from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from customers.models import Customer
from inventory.models import InventoryItem

class RentalLocation(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        validators=[RegexValidator(regex=r"^\+?[1-9]\d{1,14}$")],
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RentalOrder(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, verbose_name="Товар")
    location = models.ForeignKey('admin_panel.RentalLocation', on_delete=models.CASCADE, verbose_name="Магазин")  # Строковая ссылка на RentalLocation
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Клиент")
    rental_start_date = models.DateField(verbose_name="Дата начала аренды")
    rental_end_date = models.DateField(verbose_name="Дата окончания аренды")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена", editable=False)
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        ordering = ["-rental_start_date"]

    def clean(self):
        if self.rental_start_date and self.rental_end_date:
            if self.rental_start_date >= self.rental_end_date:
                raise ValidationError("Дата окончания аренды должна быть позже даты начала.")
        super().clean()

    def save(self, *args, **kwargs):
        if self.rental_start_date and self.rental_end_date:
            rental_days = (self.rental_end_date - self.rental_start_date).days
            self.total_price = self.item.price_per_day * rental_days

        with transaction.atomic():
            if self.is_active:
                stock = InventoryStock.objects.get(item=self.item, location=self.location)
                if stock.available_quantity > 0:
                    stock.available_quantity -= 1
                    stock.save()
                else:
                    raise ValueError("Недостаточное количество доступного товара.")
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.customer.name}"
