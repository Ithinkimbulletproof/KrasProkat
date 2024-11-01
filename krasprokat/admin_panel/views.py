from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from admin_panel.forms import RentalLocationForm
from admin_panel.models import RentalLocation
from customers.models import Customer, Profile
from inventory.forms import CategoryForm, InventoryItemForm
from inventory.models import Category, InventoryStock
from main.views import is_admin


@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/admin_dashboard.html')

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "admin_panel/customer_list.html", {"customers": customers})

def create_location(request):
    if request.method == 'POST':
        form = RentalLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RentalLocationForm()
    return render(request, 'admin_panel/create_location.html', {'form': form})

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
    return render(request, "admin_panel/create_seller.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория успешно создана!")
            return redirect('category_list')
        else:
            messages.error(request, "Ошибка при создании категории. Проверьте введенные данные.")
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect('category_list')
    return render(request, 'admin_panel/category_confirm_delete.html', {'category': category})

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
            return redirect("inventory_location_choice")
    else:
        form = InventoryItemForm()
    return render(request, "admin_panel/category_inventory_management.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def category_inventory_management(request):
    if request.method == "POST" and 'category_create' in request.POST:
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Категория успешно создана!")
            return redirect('category_inventory_management')
    else:
        category_form = CategoryForm()

    if request.method == "POST" and 'add_inventory' in request.POST:
        inventory_form = InventoryItemForm(request.POST, request.FILES)
        if inventory_form.is_valid():
            inventory_item = inventory_form.save()
            for location in RentalLocation.objects.all():
                InventoryStock.objects.create(
                    item=inventory_item,
                    location=location,
                    total_quantity=0,
                    available_quantity=0,
                )
            return redirect("inventory_location_choice")
    else:
        inventory_form = InventoryItemForm()

    categories = Category.objects.all()
    return render(request, "admin_panel/category_inventory_management.html", {
        "category_form": category_form,
        "inventory_form": inventory_form,
        "categories": categories,
    })

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
                return redirect("inventory_list_by_location", location_id=stock.location.id)
            else:
                error_message = "Общее количество не может быть меньше доступного."
        except ValueError:
            error_message = "Введите допустимое числовое значение."
        return render(request, "admin_panel/update_inventory_stock.html", {"stock": stock, "error": error_message})
    return render(request, "admin_panel/update_inventory_stock.html", {"stock": stock})
