from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="customer_profile")
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        validators=[RegexValidator(regex=r"^\+?[1-9]\d{1,14}$")],
    )
    email = models.EmailField(blank=True, verbose_name="Email", unique=True)
    address = models.TextField(blank=True, verbose_name="Адрес")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin_panel', 'Админ'),
        ('seller', 'Продавец'),
        ('customer', 'Покупатель'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
