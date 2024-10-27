from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import InventoryItem, InventoryStock, RentalOrder, Customer, RentalLocation, Profile
from .forms import InventoryItemForm, RentalOrderForm, CustomerForm

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.role == 'seller'

def home(request):
    return render(request, "main/home.html")

def inventory_list(request):
    stocks = InventoryStock.objects.select_related("item", "location")
    return render(request, "main/inventory_list.html", {"stocks": stocks})

@login_required
@user_passes_test(is_admin)
def add_inventory_item(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            inventory_item = form.save()
            for location in RentalLocation.objects.all():
                InventoryStock.objects.create(
                    item=inventory_item,
                    location=location,
                    total_quantity=0,
                    available_quantity=0,
                )
            return redirect("inventory_list")
    else:
        form = InventoryItemForm()
    return render(request, "main/add_inventory_item.html", {"form": form})

def inventory_detail(request, pk):
    stock = get_object_or_404(InventoryStock, pk=pk)
    return render(request, "main/inventory_detail.html", {"stock": stock})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "main/customer_list.html", {"customers": customers})

def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "main/add_customer.html", {"form": form})

def rental_order_list(request):
    orders = RentalOrder.objects.select_related("item", "customer", "location")
    return render(request, "main/rental_order_list.html", {"orders": orders})

def create_rental_order(request):
    if request.method == "POST":
        form = RentalOrderForm(request.POST)
        if form.is_valid():
            rental_order = form.save(commit=False)
            stock = InventoryStock.objects.get(
                item=rental_order.item, location=rental_order.location
            )
            if stock.available_quantity > 0:
                rental_order.save()
                stock.available_quantity -= 1
                stock.save()
                return redirect("rental_order_list")
            else:
                form.add_error(None, "Недостаточное количество доступного товара")
    else:
        form = RentalOrderForm()
    return render(request, "main/create_rental_order.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def update_inventory_stock(request, stock_id):
    stock = get_object_or_404(InventoryStock, id=stock_id)
    if request.method == "POST":
        new_total_quantity = request.POST.get("total_quantity")
        try:
            new_total_quantity = int(new_total_quantity)
            if new_total_quantity >= stock.available_quantity:
                stock.total_quantity = new_total_quantity
                stock.save()
                return redirect("inventory_list")
            else:
                error_message = "Общее количество не может быть меньше доступного."
                return render(
                    request,
                    "main/update_inventory_stock.html",
                    {"stock": stock, "error": error_message},
                )
        except ValueError:
            error_message = "Введите допустимое числовое значение."
            return render(
                request,
                "main/update_inventory_stock.html",
                {"stock": stock, "error": error_message},
            )
    return render(request, "main/update_inventory_stock.html", {"stock": stock})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Назначение роли клиенту при регистрации
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

@login_required
def customer_account(request):
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, "main/customer_account.html", {"customer": customer})

@login_required
def customer_rentals(request):
    customer = get_object_or_404(Customer, user=request.user)
    rentals = RentalOrder.objects.filter(customer=customer)
    return render(request, "main/customer_rentals.html", {"rentals": rentals})

@login_required
@user_passes_test(is_admin)
def create_seller(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Назначение роли продавца
            Profile.objects.create(user=user, role='seller')
            return redirect("customer_list")
    else:
        form = UserCreationForm()
    return render(request, "main/create_seller.html", {"form": form})
