from datetime import timedelta, datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from .models import InventoryItem, InventoryStock, RentalOrder, RentalLocation, Profile, Category, NewsItem, CarouselImage
from .forms import InventoryItemForm, CategoryForm, LocationForm, CarouselImageForm, NewsItemForm


#  Основные функции
def is_admin(user):
    """Назначение аккаунту роли администратора"""
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def is_seller(user):
    """Назначение аккаунту роли продавца"""
    return hasattr(user, 'profile') and user.profile.role == 'seller'

def home(request):
    """Домашняя страница"""
    carousel_images = CarouselImage.objects.all()
    news_items = NewsItem.objects.all().order_by('-date')[:2]
    return render(request, 'main/home.html', {'carousel_images': carousel_images, 'news_items': news_items})

def rental_terms(request):
    """Условия проката"""
    return render(request, "main/rental_terms.html")

def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query) | User.objects.filter(email__icontains=query)
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return JsonResponse(users_list, safe=False)

#  Инвентарь
@login_required
@user_passes_test(is_admin)
def inventory_add(request):
    """Добавление оборудования"""
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

def inventory_detail(request, pk):
    """Детали оборудования"""
    stock = get_object_or_404(InventoryStock, pk=pk)
    return render(request, "main/inventory_detail.html", {"stock": stock})

@login_required
@user_passes_test(is_admin)
def inventory_update(request, pk):
    """Обновление оборудования"""
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
    """Удаление оборудования"""
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        inventory_item.delete()
        return redirect("c_and_i_management")

    return render(request, "main/inventory_delete.html", {"inventory_item": inventory_item})

@login_required
def confirm_booking(request, location_id, stock_id):
    """Подтверждение бронирования"""
    print(f"Запрос в confirm_booking: {request.method}, location_id={location_id}, stock_id={stock_id}")

    stocks = []
    total_quantity = 0
    quantity = int(request.GET.get('quantity', '0')) if request.method == 'GET' else int(request.POST.get('quantity', '0'))
    print(f"Количество для бронирования: {quantity}")

    if quantity > 0:
        stock = get_object_or_404(InventoryStock, item__id=stock_id, location_id=location_id)
        stocks.append((stock, quantity))
        total_quantity += quantity

    if not stocks:
        messages.error(request, "Не выбрано ни одного инвентаря.")
        print("Инвентарь не выбран, перенаправляем на список инвентаря")
        return redirect('inventory_list', location_id=location_id)

    if not hasattr(request.user, 'profile'):
        messages.error(request, "У вас нет профиля покупателя. Пожалуйста, создайте его.")
        print("Нет профиля покупателя, перенаправляем на регистрацию")
        return redirect('register')

    customer = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        rental_start_date = request.POST.get('rental_start_date')
        rental_end_date = request.POST.get('rental_end_date')
        print(f"Получена POST-заявка с датами аренды: {rental_start_date} - {rental_end_date}")

        try:
            rental_start_date = datetime.strptime(rental_start_date, '%Y-%m-%d').date()
            rental_end_date = datetime.strptime(rental_end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Неверный формат даты.")
            print("Неверный формат даты, перенаправляем на подтверждение бронирования")
            return redirect('confirm_booking', location_id=location_id, stock_id=stock_id)

        if rental_end_date <= rental_start_date:
            messages.error(request, "Дата окончания аренды должна быть позже даты начала.")
            print("Ошибка дат: дата окончания раньше или совпадает с начальной")
            return redirect('confirm_booking', location_id=location_id, stock_id=stock_id)

        if quantity > stock.available_quantity:
            messages.error(request, f"Нельзя забронировать больше {stock.available_quantity} единиц {stock.item.name}.")
            print(f"Ошибка количества: запрошено {quantity}, доступно {stock.available_quantity}")
            return redirect('inventory_list', location_id=location_id)

        # Создание заказа и сохранение
        try:
            rental_order = RentalOrder(
                item=stock.item,
                location=stock.location,
                customer=customer,
                rental_start_date=rental_start_date,
                rental_end_date=rental_end_date,
                is_active=True
            )
            rental_order.save()  # Вызовет метод save() модели
            print(f"Заказ создан: {rental_order}")

            # Обновление количества на складе
            stock.available_quantity -= quantity
            stock.save()
            print("Обновлено количество на складе")

            messages.success(request, "Бронь успешно создана.")
            return redirect('rentals')
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")
            messages.error(request, "Не удалось создать заказ. Попробуйте еще раз.")

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    print("GET-запрос: Отображение страницы подтверждения бронирования")
    return render(request, "main/confirm_booking.html", {
        "stocks": stocks,
        "total_quantity": total_quantity,
        "today": today,
        "tomorrow": tomorrow,
        "location_id": location_id,
    })

#  Клиенты
def inventory_location_choice(request):
    """Выбор магазина для просмотра инвентаря"""
    locations = RentalLocation.objects.all()
    return render(request, "main/inventory_location_choice.html", {"locations": locations})

def inventory_list(request, location_id):
    """Просмотр инвентаря на выбранном магазине"""
    location = get_object_or_404(RentalLocation, id=location_id)
    stocks = InventoryStock.objects.filter(location=location)

    for stock in stocks:
        quantity = request.GET.get(f'quantity-{stock.item.id}', '0')
        stock.selected_quantity = int(quantity)

    return render(request, "main/inventory_list.html", {
        "stocks": stocks,
        "location": location,
    })

#  Личный кабинет покупателя
@login_required
def customer_account(request):
    """Личный кабинет"""
    customer, created = Profile.objects.get_or_create(user=request.user)

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
def rentals(request):
    """История броней"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('registration')

    if profile.role == 'customer':
        rental_orders = RentalOrder.objects.filter(customer=profile.location).order_by('-rental_start_date')
    elif profile.role == 'seller':
        rental_orders = RentalOrder.objects.filter(location=profile.location).order_by('-rental_start_date')
    else:
        rental_orders = RentalOrder.objects.filter(location=profile.location).order_by('-rental_start_date')

    return render(request, 'main/rentals.html', {'rental_orders': rental_orders})

#  Регистрация и вход
def register(request):
    """Регистрация"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            Profile.objects.create(
                user=user,
                role='customer',
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, "main/register.html", {"form": form})

def user_login(request):
    """Вход"""
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

#  Инструменты администратора
@login_required
def admin_dashboard(request):
    """Панель администратора"""
    return render(request, 'main/admin_dashboard.html')

@login_required
@user_passes_test(is_admin)
def category_inventory_management(request):
    """Управление категориями и инвентарём"""
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
def create_seller(request):
    """Создание продавца"""
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
    """Редактирование продавца"""
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
    """Удаление продавца"""
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

def create_location(request):
    """Создание магазина"""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_location')

    else:
        form = LocationForm()

    stores = RentalLocation.objects.all()

    return render(request, 'main/create_location.html', {'form': form, 'stores': stores})

@user_passes_test(is_admin)
def add_inventory_to_store(request, location_id):
    """Добавление товара в магазин"""
    location = get_object_or_404(RentalLocation, id=location_id)
    inventory_items = InventoryItem.objects.all()
    inventory_stocks = InventoryStock.objects.filter(location=location).select_related('item')
    stock_dict = {stock.item.id: stock for stock in inventory_stocks}

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        stock, created = InventoryStock.objects.get_or_create(item_id=item_id, location=location)

        if action == 'increase':
            stock.total_quantity += 1
            stock.available_quantity += 1
        elif action == 'decrease':
            if stock.available_quantity > 0:
                stock.available_quantity -= 1
            if stock.total_quantity > 0:
                stock.total_quantity -= 1

        try:
            stock.full_clean()
            stock.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'item_id': item_id,
                    'available_quantity': stock.available_quantity,
                    'total_quantity': stock.total_quantity,
                })
            return redirect(reverse('store_inventory', args=[location_id]))
        except ValidationError as e:
            error_message = e.messages[0]

    return render(request, 'main/add_inventory_to_store.html', {
        'location': location,
        'inventory_items': inventory_items,
        'stock_dict': stock_dict,
        'error_message': error_message if 'error_message' in locals() else None
    })

@login_required
@user_passes_test(is_admin)
def category_create(request):
    """Создание категории"""
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
    """Редактирование категории"""
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
    """Удаление категории"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect('c_and_i_management')
    return render(request, 'main/category_confirm_delete.html', {'category': category})

def manage_carousel(request):
    """Управление каруселью"""
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
    """Управление новостями"""
    if request.method == "POST":
        form = NewsItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_news')
    else:
        form = NewsItemForm()

    news_items = NewsItem.objects.all()
    return render(request, 'main/manage_news.html', {'form': form, 'news_items': news_items})

#  Инструменты продавца
def seller_dashboard(request):
    """Панель продавца"""
    profile = request.user.profile
    location = profile.location

    inventory = InventoryStock.objects.filter(location=location)

    today = timezone.now().date()
    today_returns = RentalOrder.objects.filter(
        location=location,
        rental_end_date=today,
        is_active=True
    )

    context = {
        'location': location,
        'inventory': inventory,
        'today_returns': today_returns,
    }
    return render(request, 'main/seller_dashboard.html', context)
