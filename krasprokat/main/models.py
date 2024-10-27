from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Админ'),
        ('seller', 'Продавец'),
        ('customer', 'Покупатель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


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


class InventoryItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.CharField(max_length=100, verbose_name="Категория")
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за день"
    )
    image = models.ImageField(
        upload_to="inventory_images/", blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryStock(models.Model):
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, verbose_name="Товар"
    )
    location = models.ForeignKey(
        RentalLocation, on_delete=models.CASCADE, verbose_name="Магазин"
    )
    total_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Общее количество"
    )
    available_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Доступное количество"
    )

    class Meta:
        unique_together = ("item", "location")
        ordering = ["item"]

    def __str__(self):
        return f"{self.item.name} ({self.location.name}) - {self.available_quantity}/{self.total_quantity}"


class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        validators=[RegexValidator(regex=r"^\+?[1-9]\d{1,14}$")],
    )
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Адрес")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RentalOrder(models.Model):
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, verbose_name="Товар"
    )
    location = models.ForeignKey(
        RentalLocation, on_delete=models.CASCADE, verbose_name="Магазин"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="Клиент"
    )
    rental_start_date = models.DateField(verbose_name="Дата начала аренды")
    rental_end_date = models.DateField(verbose_name="Дата окончания аренды")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Итоговая цена", editable=False
    )
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        ordering = ["-rental_start_date"]

    def save(self, *args, **kwargs):
        if self.rental_start_date and self.rental_end_date:
            rental_days = (self.rental_end_date - self.rental_start_date).days
            self.total_price = self.item.price_per_day * rental_days
        if self.is_active:
            stock = InventoryStock.objects.get(item=self.item, location=self.location)
            stock.available_quantity -= 1
            stock.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.customer.name}"
