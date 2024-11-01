from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import rental_terms

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path('rental-terms/', rental_terms, name='rental_terms'),  # Условия проката
    path("register/", views.register, name="register"),  # Регистрация
    path("login/", views.user_login, name="login"),  # Вход
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name="logout"),  # Выход
]
