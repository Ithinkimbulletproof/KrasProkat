from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import InventoryItem, InventoryStock, RentalOrder, Customer, RentalLocation, Profile, Category, NewsItem, CarouselImage
from .forms import InventoryItemForm, RentalOrderForm, CustomerForm, RentalLocationForm, CategoryForm, LocationForm, CarouselImageForm, NewsItemForm


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.role == 'seller'

def home(request):
    carousel_images = CarouselImage.objects.all()
    news_items = NewsItem.objects.all().order_by('-date')[:2]
    return render(request, 'main/home.html', {'carousel_images': carousel_images, 'news_items': news_items})

def manage_carousel(request):
    if request.method == "POST":
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_carousel')
    else:
        form = CarouselImageForm()

    carousel_images = CarouselImage.objects.all()
    return render(request, 'main/manage_carousel.html', {'form': form, 'carousel_images': carousel_images})

def manage_news(request):
    if request.method == "POST":
        form = NewsItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_news')
    else:
        form = NewsItemForm()

    news_items = NewsItem.objects.all()
    return render(request, 'main/manage_news.html', {'form': form, 'news_items': news_items})

def rental_terms(request):
    return render(request, "main/rental_terms.html")

def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query) | User.objects.filter(email__icontains=query)
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return JsonResponse(users_list, safe=False)

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
    })


@login_required
@user_passes_test(is_admin)
def category_inventory_management(request):
    categories = Category.objects.all()
    inventory_items = InventoryItem.objects.all()

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

    stocks = InventoryStock.objects.filter(item=inventory_item)
    stock = stocks.first() if stocks.count() == 1 else None

    error_message = None

    if request.method == "POST":
        form = InventoryItemForm(request.POST, request.FILES, instance=inventory_item)
        new_total_quantity = request.POST.get("update_quantity")

        if not stock:
            location_id = request.POST.get("location")
            if location_id:
                location = get_object_or_404(RentalLocation, pk=location_id)
                stock = InventoryStock.objects.get(item=inventory_item, location=location)

        try:
            if form.is_valid() and stock:
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
        "stocks": stocks,
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
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if first_name:
            customer.first_name = first_name
        if last_name:
            customer.last_name = last_name

        customer.email = email
        customer.phone = phone
        customer.address = address
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
        user_id = request.POST.get("user_id")
        location_id = request.POST.get("location_id")

        if not user_id or not location_id:
            return redirect("create_seller")

        try:
            user = User.objects.get(id=int(user_id))
            location = RentalLocation.objects.get(id=int(location_id))
        except (User.DoesNotExist, RentalLocation.DoesNotExist, ValueError):
            return redirect("create_seller")

        profile, created = Profile.objects.get_or_create(user=user)

        profile.role = 'seller'
        profile.location = location
        profile.save()

        return redirect("create_seller")

    users = User.objects.exclude(is_superuser=True).exclude(profile__role='admin')
    locations = RentalLocation.objects.all()
    sellers = Profile.objects.filter(role='seller')

    return render(request, "main/create_seller.html", {
        "users": users,
        "locations": locations,
        "sellers": sellers,
    })

@login_required
@user_passes_test(is_admin)
def edit_seller(request, user_id):
    if request.method == "POST":
        location_id = request.POST.get("location_id")

        try:
            profile = Profile.objects.get(user_id=user_id)
            location = RentalLocation.objects.get(id=location_id)
            profile.location = location
            profile.save()
            return redirect("create_seller")
        except (Profile.DoesNotExist, RentalLocation.DoesNotExist):
            return render(request, "main/edit_seller.html", {
                'error_message': 'Профиль или магазин не найдены.',
                'user_id': user_id,
                'locations': RentalLocation.objects.all(),
                'profile': profile
            })

    try:
        profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        return render(request, "main/edit_seller.html", {
            'error_message': 'Профиль не найден.',
        })

    return render(request, "main/edit_seller.html", {
        'profile': profile,
        'locations': RentalLocation.objects.all(),
    })

@login_required
@user_passes_test(is_admin)
def delete_seller(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")

        try:
            profile = Profile.objects.get(user_id=user_id)
            profile.delete()
            messages.success(request, "Продавец успешно удален.")
        except Profile.DoesNotExist:
            messages.error(request, "Профиль продавца не найден.")
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")

    return redirect("create_seller")

@login_required
def admin_dashboard(request):
    return render(request, 'main/admin_dashboard.html')


def create_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_location')

    else:
        form = LocationForm()

    stores = RentalLocation.objects.all()

    return render(request, 'main/create_location.html', {'form': form, 'stores': stores})

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
