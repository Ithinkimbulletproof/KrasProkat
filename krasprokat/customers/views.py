from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from admin_panel.models import RentalOrder
from customers.models import Customer


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

    return render(request, "customers/customer_account.html", {"customer": customer})

@login_required
def customer_rentals(request):
    customer = get_object_or_404(Customer, user=request.user)
    rentals = RentalOrder.objects.filter(customer=customer)
    return render(request, "customers/customer_rentals.html", {"rentals": rentals})
