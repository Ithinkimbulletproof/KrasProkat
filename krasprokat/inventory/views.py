from django.shortcuts import render, get_object_or_404, redirect
from admin_panel.forms import RentalOrderForm
from admin_panel.models import RentalLocation, RentalOrder
from inventory.models import InventoryStock
from main.views import is_admin


def inventory_location_choice(request):
    locations = RentalLocation.objects.all()
    return render(request, "inventory/inventory_location_choice.html", {"locations": locations})

def inventory_list(request, location_id):
    location = get_object_or_404(RentalLocation, id=location_id)
    stocks = InventoryStock.objects.filter(location=location)
    return render(request, "inventory/inventory_list.html", {
        "stocks": stocks,
        "location": location,
        "can_add_inventory": request.user.is_authenticated and is_admin(request.user)
    })

def inventory_detail(request, pk):
    stock = get_object_or_404(InventoryStock, pk=pk)
    return render(request, "inventory/inventory_detail.html", {"stock": stock})

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
    return render(request, "inventory/create_rental_order.html", {"form": form})

def rental_order_list(request):
    orders = RentalOrder.objects.select_related("item", "customer", "location")
    return render(request, "inventory/rental_order_list.html", {"orders": orders})
