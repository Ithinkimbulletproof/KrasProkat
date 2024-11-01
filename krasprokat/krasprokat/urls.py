from django.contrib import admin
from django.urls import path
from django.urls import include


urlpatterns = [
    path("admin_panel/", admin.site.urls),
    path("", include("main.urls")),  # Главная страница и авторизация
    path("inventory/", include("inventory.urls")),  # Инвентарь
    path("customers/", include("customers.urls")),  # Клиенты
    path("admin_panel-panel/", include("admin_panel.urls")),  # Панель админа
]
