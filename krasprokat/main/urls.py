from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import rental_terms

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path('rental-terms/', rental_terms, name='rental_terms'),  # Условия проката

    # Инвентарь
    path("inventory_add/", views.inventory_add, name="inventory_add"),  # Добавление инвентаря
    path("inventory/detail/<int:pk>/", views.inventory_detail, name="inventory_detail"),  # Детали инвентаря
    path('inventory/update/<int:pk>/', views.inventory_update, name='inventory_update'),  # Обновление инвентаря
    path('inventory/delete/<int:pk>/', views.inventory_delete, name='inventory_delete'),  # Удаление инвентаря
    path('inventory/confirm_booking/<int:location_id>/<int:stock_id>/', views.confirm_booking, name='confirm_booking'),  # Подтверждение брони

    # Клиенты
    path('inventory/location/', views.inventory_location_choice, name='inventory_location_choice'),  # Выбор магазина для просмотра инвентаря
    path('inventory/<int:location_id>/', views.inventory_list, name='inventory_list'),  # Просмотр инвентаря на выбранном магазине

    # Личный кабинет покупателя
    path("account/", views.customer_account, name="customer_account"),  # Личный кабинет покупателя
    path("rentals", views.rentals, name="rentals"),  # История броней

    # Регистрация и вход
    path("register/", views.register, name="register"),  # Регистрация
    path("login/", views.user_login, name="login"),  # Вход
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name="logout"),  # Выход

    # Инструменты админа
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Панель админа
    path("admin_dashboard/c_and_i_management", views.category_inventory_management, name="c_and_i_management"),  # Управление категориями и инвентарём
    path("admin_dashboard/create_seller/", views.create_seller, name="create_seller"),  # Создание продавца
    path("admin_dashboard/edit_seller/<int:user_id>/", views.edit_seller, name="edit_seller"),  # Редактирование продавца
    path("admin_dashboard/delete_seller/", views.delete_seller, name="delete_seller"),  # Удаление продавца
    path('admin_dashboard/create-location/', views.create_location, name='create_location'),  # Создание магазина
    path('store/<int:location_id>/add_inventory/', views.add_inventory_to_store, name='add_inventory_to_store'),  # Добавление товара в магазин
    path("admin_dashboard/categories_add/", views.category_create, name="category_create"),  # Создание категории
    path("admin_dashboard/categories_update/<int:pk>/", views.category_update, name="category_update"),  # Обновление категории
    path("admin_dashboard/categories_delete/<int:pk>/", views.category_delete, name="category_delete"),  # Удаление категории
    path('admin_dashboard/manage-carousel/', views.manage_carousel, name='manage_carousel'),  # Управление каруселью
    path('admin_dashboard/manage-news/', views.manage_news, name='manage_news'),  # Управление новостями

    # Инструменты продавца
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),  # Панель продавца
]
