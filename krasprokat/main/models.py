from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class RentalLocation(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название магазина")
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

class Profile(models.Model):
    ROLE_CHOICES = [('admin', 'Админ'), ('seller', 'Продавец'), ('customer', 'Покупатель')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    location = models.ForeignKey(
        RentalLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Магазин",
        help_text="Привязанный магазин для продавца"
    )
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    email = models.EmailField(verbose_name="Email", unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

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
    location = models.ForeignKey(RentalLocation, on_delete=models.SET_NULL, verbose_name="Магазин", null=True)
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

class RentalOrder(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, verbose_name="Товар")
    location = models.ForeignKey(RentalLocation, on_delete=models.CASCADE, verbose_name="Магазин")
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Клиент", limit_choices_to={'role': 'customer'})
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
        """Переопределенный метод save для обработки доступного количества"""
        if self.rental_start_date and self.rental_end_date:
            rental_days = (self.rental_end_date - self.rental_start_date).days
            self.total_price = self.item.price_per_day * rental_days

        with transaction.atomic():
            if self.is_active:
                stock = InventoryStock.objects.select_for_update().get(item=self.item, location=self.location)
                if stock.available_quantity >= 1:
                    stock.available_quantity -= 1
                    stock.save()
                    print(f"Склад обновлен: {stock}")
                else:
                    raise ValueError("Недостаточное количество доступного товара.")
            super().save(*args, **kwargs)

    def __str__(self):
        customer_name = f"{self.customer.first_name} {self.customer.last_name}".strip()
        return f"{self.item.name} - {customer_name if customer_name else 'Имя не указано'}"

class CarouselImage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='carousel/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class NewsItem(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[('news', 'Новости'), ('promo', 'Акции')])

    def __str__(self):
        return f"{self.title} ({self.category})"
