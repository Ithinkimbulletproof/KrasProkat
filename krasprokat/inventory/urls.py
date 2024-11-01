from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("inventory/", views.inventory_location_choice, name="inventory_location_choice"),  # Выбор магазина
    path("inventory/<int:location_id>/", views.inventory_list, name="inventory_list_by_location"),  # Список инвентаря для выбранного магазина
    path("inventory/detail/<int:pk>/", views.inventory_detail, name="inventory_detail"),  # Детали инвентаря
    path("orders/", views.rental_order_list, name="rental_order_list"),  # Список заказов
    path("orders/create/", views.create_rental_order, name="create_rental_order"),  # Создание заказа
]
