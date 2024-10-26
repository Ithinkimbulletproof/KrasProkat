from django.shortcuts import render, get_object_or_404, redirect
from .models import InventoryItem, RentalOrder, Customer
from .forms import InventoryItemForm, RentalOrderForm, CustomerForm


# Главная страница
def home(request):
    return render(request, "main/home.html")


# Список инвентаря
def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, "main/inventory_list.html", {"items": items})


# Добавление инвентаря
def add_inventory_item(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("inventory_list")
    else:
        form = InventoryItemForm()
    return render(request, "main/add_inventory_item.html", {"form": form})


# Детали инвентаря
def inventory_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    return render(request, "main/inventory_detail.html", {"item": item})


# Список клиентов
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "main/customer_list.html", {"customers": customers})


# Добавление клиента
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "main/add_customer.html", {"form": form})


# Список заказов
def rental_order_list(request):
    orders = RentalOrder.objects.select_related("item", "customer")
    return render(request, "main/rental_order_list.html", {"orders": orders})


# Создание заказа с проверкой доступного количества и обновлением
def create_rental_order(request):
    if request.method == "POST":
        form = RentalOrderForm(request.POST)
        if form.is_valid():
            rental_order = form.save(commit=False)
            item = rental_order.item
            if item.available_quantity > 0:
                rental_order.save()
                item.available_quantity -= 1
                item.save()
                return redirect("rental_order_list")
            else:
                form.add_error(None, "Недостаточное количество доступного товара")
    else:
        form = RentalOrderForm()
    return render(request, "main/create_rental_order.html", {"form": form})
