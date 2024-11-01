from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from customers.models import Profile


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin_panel'

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.role == 'seller'

def home(request):
    return render(request, "main/home.html")

def rental_terms(request):
    return render(request, "main/rental_terms.html")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role='customer')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, "main/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error_message = "Неправильное имя пользователя или пароль."
            return render(request, "main/login.html", {"error": error_message})
    return render(request, "main/login.html")


