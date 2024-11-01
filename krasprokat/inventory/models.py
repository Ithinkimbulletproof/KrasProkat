from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.description[:50]}..." if self.description else self.name


class InventoryItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за день")
    image = models.ImageField(upload_to="inventory_images/", blank=True, null=True, verbose_name="Изображение")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryStock(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, verbose_name="Товар")
    location = models.ForeignKey('admin_panel.RentalLocation', on_delete=models.CASCADE, verbose_name="Магазин")
    total_quantity = models.PositiveIntegerField(default=0, verbose_name="Общее количество")
    available_quantity = models.PositiveIntegerField(default=0, verbose_name="Доступное количество")

    class Meta:
        unique_together = ("item", "location")
        ordering = ["item"]

    def clean(self):
        if self.total_quantity < self.available_quantity:
            raise ValidationError("Общее количество не может быть меньше доступного.")
        super().clean()

    def __str__(self):
        return f"{self.item.name} ({self.location.name}) - {self.available_quantity}/{self.total_quantity}"
