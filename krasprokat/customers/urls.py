from django.urls import path
from . import views


urlpatterns = [
    path("account/", views.customer_account, name="customer_account"),  # Личный кабинет покупателя
    path("account/rentals/", views.customer_rentals, name="customer_rentals"),  # История броней
]
