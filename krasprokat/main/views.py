from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import InventoryItem, InventoryStock, RentalOrder, Customer, RentalLocation, Profile, Category
from .forms import InventoryItemForm, RentalOrderForm, CustomerForm, RentalLocationForm, CategoryForm

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.role == 'seller'

def home(request):
    return render(request, "main/home.html")

def rental_terms(request):
    return render(request, "main/rental_terms.html")

@login_required
@user_passes_test(is_admin)
def inventory_add(request):
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
            return redirect("c_and_i_management")
    else:
        form = InventoryItemForm()
    return render(request, "main/inventory_add.html", {"form": form})

def inventory_location_choice(request):
    locations = RentalLocation.objects.all()
    return render(request, "main/inventory_location_choice.html", {"locations": locations})

def inventory_list(request, location_id):
    location = get_object_or_404(RentalLocation, id=location_id)
    stocks = InventoryStock.objects.filter(location=location)
    return render(request, "main/inventory_list.html", {
        "stocks": stocks,
        "location": location,
        "can_add_inventory": request.user.is_authenticated and is_admin(request.user)
    })


@login_required
@user_passes_test(is_admin)
def category_inventory_management(request):
    categories = Category.objects.all()  # Получаем все категории
    inventory_items = InventoryItem.objects.all()  # Получаем все товары

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
            return redirect("inventory_location_choice")
    else:
        form = InventoryItemForm()

    return render(request, "main/category_inventory_management.html", {
        "form": form,
        "categories": categories,
        "inventory_items": inventory_items,
    })


@login_required
@user_passes_test(is_admin)
def inventory_update(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    stock = get_object_or_404(InventoryStock, item=inventory_item)

    error_message = None

    if request.method == "POST":
        form = InventoryItemForm(request.POST, request.FILES, instance=inventory_item)
        new_total_quantity = request.POST.get("update_quantity")

        try:
            if form.is_valid():
                form.save()

                new_total_quantity = int(new_total_quantity)
                if new_total_quantity >= stock.available_quantity:
                    stock.total_quantity = new_total_quantity
                    stock.save()
                    return redirect("c_and_i_management")
                else:
                    error_message = "Общее количество не может быть меньше доступного."
        except ValueError:
            error_message = "Введите допустимое числовое значение."

    else:
        form = InventoryItemForm(instance=inventory_item)

    return render(request, "main/inventory_update.html", {
        "form": form,
        "inventory_item": inventory_item,
        "stock": stock,
        "error": error_message,
    })

@login_required
@user_passes_test(is_admin)
def inventory_delete(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        inventory_item.delete()
        return redirect("c_and_i_management")

    return render(request, "main/inventory_delete.html", {"inventory_item": inventory_item})


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
            stock = InventoryStock.objects.get(item=rental_order.item, location=rental_order.location)
            if stock.available_quantity > 0:
                rental_order.save()
                stock.available_quantity -= 1
                stock.save()
                return redirect("rental_order_list")
            else:
                form.add_error(None, "Недостаточное количество доступного товара.")
    else:
        form = RentalOrderForm()
    return render(request, "main/create_rental_order.html", {"form": form})

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

@login_required
def customer_account(request):
    customer, created = Customer.objects.get_or_create(user=request.user)

    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.email = request.POST.get("email")
        customer.phone = request.POST.get("phone")
        customer.address = request.POST.get("address")
        customer.save()
        return redirect("customer_account")

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
            Profile.objects.create(user=user, role='seller')
            return redirect("customer_list")
    else:
        form = UserCreationForm()
    return render(request, "main/create_seller.html", {"form": form})

@login_required
def admin_dashboard(request):
    return render(request, 'main/admin_dashboard.html')

def create_location(request):
    if request.method == 'POST':
        form = RentalLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RentalLocationForm()
    return render(request, 'main/create_location.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('c_and_i_management')
    else:
        form = CategoryForm()
    return render(request, 'main/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('c_and_i_management')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'main/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect('c_and_i_management')
    return render(request, 'main/category_confirm_delete.html', {'category': category})
