from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import rental_terms

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path('rental-terms/', rental_terms, name='rental_terms'),  # Условия проката

    # Инвентарь
    path("inventory/", views.inventory_location_choice, name="inventory_location_choice"),  # Выбор магазина
    path("inventory/<int:location_id>/", views.inventory_list, name="inventory_list_by_location"),  # Список инвентаря для выбранного магазина
    path("inventory/detail/<int:pk>/", views.inventory_detail, name="inventory_detail"),  # Детали инвентаря
    path("inventory/add/", views.add_inventory_item, name="add_inventory_item"),  # Добавление инвентаря
    path("inventory/update/<int:stock_id>/", views.update_inventory_stock, name="update_inventory_stock"),  # Обновление инвентаря

    # Клиенты
    path("customers/", views.customer_list, name="customer_list"),  # Список клиентов
    path("customers/add/", views.add_customer, name="add_customer"),  # Добавление клиента

    # Заказы
    path("orders/", views.rental_order_list, name="rental_order_list"),  # Список заказов
    path("orders/create/", views.create_rental_order, name="create_rental_order"),  # Создание заказа

    # Личный кабинет покупателя
    path("account/", views.customer_account, name="customer_account"),  # Личный кабинет покупателя
    path("account/rentals/", views.customer_rentals, name="customer_rentals"),  # История броней

    # Регистрация и вход
    path("register/", views.register, name="register"),  # Регистрация
    path("login/", views.user_login, name="login"),  # Вход
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name="logout"),  # Выход

    # Инструменты админа
    path("account/create_seller/", views.create_seller, name="create_seller"),  # Создание продавца
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Панель админа
    path('create-location/', views.create_location, name='create_location'),  # Создание магазина

    # Управление категориями
    path("categories/", views.category_list, name="category_list"),  # Список категорий
    path("categories/add/", views.category_create, name="category_create"),  # Создание категории
    path("categories/update/<int:pk>/", views.category_update, name="category_update"),  # Обновление категории
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),  # Удаление категории
]
