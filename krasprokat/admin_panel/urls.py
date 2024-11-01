from django.urls import path
from . import views


urlpatterns = [
    path('admin_panel-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Панель админа
    path("customers/", views.customer_list, name="customer_list"),  # Список клиентов
    path('create-location/', views.create_location, name='create_location'),  # Создание магазина
    path("account/create_seller/", views.create_seller, name="create_seller"),  # Создание продавца
    path("categories/add/", views.category_create, name="category_create"),  # Создание категории
    path("categories/update/<int:pk>/", views.category_update, name="category_update"),  # Обновление категории
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),  # Удаление категории
    path("inventory/add/", views.add_inventory_item, name="add_inventory_item"),  # Добавление инвентаря
    path("categories/inventory/", views.category_inventory_management, name="category_inventory_management"),  # Управление категориями и инвентарем
    path("inventory/update/<int:stock_id>/", views.update_inventory_stock, name="update_inventory_stock"),  # Обновление инвентаря
]
