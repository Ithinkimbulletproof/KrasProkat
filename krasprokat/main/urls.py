from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    # Инвентарь
    path("inventory/", views.inventory_list, name="inventory_list"),  # Список инвентаря
    path(
        "inventory/<int:pk>/", views.inventory_detail, name="inventory_detail"
    ),  # Детали инвентаря
    path(
        "inventory/add/", views.add_inventory_item, name="add_inventory_item"
    ),  # Добавление инвентаря
    # Клиенты
    path("customers/", views.customer_list, name="customer_list"),  # Список клиентов
    path(
        "customers/add/", views.add_customer, name="add_customer"
    ),  # Добавление клиента
    # Заказы
    path(
        "orders/", views.rental_order_list, name="rental_order_list"
    ),  # Список заказов
    path(
        "orders/create/", views.create_rental_order, name="create_rental_order"
    ),  # Создание заказа
    # Личный кабинет покупателя
    path(
        "account/", views.customer_account, name="customer_account"
    ),  # Личный кабинет покупателя
    path(
        "account/rentals/", views.customer_rentals, name="customer_rentals"
    ),  # История броней
]
