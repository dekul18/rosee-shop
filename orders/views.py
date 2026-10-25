import json
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import cart_items
from .forms import CheckoutForm
from .models import Order, OrderItem


@require_POST
def add(request):
    try:
        data = json.loads(request.body)
        pid, qty = int(data["id"]), max(1, int(data.get("qty", 1)))
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "Invalid request."}, status=400)
    p = get_object_or_404(Product, pk=pid, is_active=True)
    size, color = str(data.get("size", ""))[:20], str(data.get("color", ""))[:40]
    if "|" in size + color:
        return JsonResponse({"error": "Invalid option."}, status=400)
    if (p.size_list and size not in p.size_list) or (p.color_list and color not in p.color_list):
        return JsonResponse({"error": "Please pick a size and a color."}, status=400)
    cart = request.session.get("cart", {})
    key = f"{pid}|{size}|{color}"
    in_cart = sum(q for k, q in cart.items() if k.startswith(f"{pid}|"))
    if in_cart + qty > p.stock:
        return JsonResponse({"error": f"Only {p.stock} left in stock."}, status=400)
    cart[key] = cart.get(key, 0) + qty
    request.session["cart"] = cart
    return JsonResponse({"count": sum(cart.values())})


def cart(request):
    if request.method == "POST":
        key, cart = request.POST.get("key", ""), request.session.get("cart", {})
        if key in cart:
            if request.POST.get("action") == "remove":
                del cart[key]
            else:
                try:
                    qty = int(request.POST.get("qty", 1))
                except ValueError:
                    qty = 1
                if qty < 1:
                    del cart[key]
                else:
                    cart[key] = qty
            request.session["cart"] = cart
        return redirect("orders:cart")
    items, total = cart_items(request)
    return render(request, "orders/cart.html", {"items": items, "total": total, "form": CheckoutForm()})


@require_POST
def checkout(request):
    items, total = cart_items(request)
    if not items:
        return redirect("orders:cart")
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return render(request, "orders/cart.html", {"items": items, "total": total, "form": form})
    with transaction.atomic():
        # Lock the rows so two buyers can't take the last piece at the same time.
        locked = Product.objects.select_for_update().in_bulk([i["product"].pk for i in items])
        for i in items:
            if i["qty"] > locked[i["product"].pk].stock:
                messages.error(request, f"Sorry, only {locked[i['product'].pk].stock} left of {i['product'].name}.")
                return redirect("orders:cart")
        order = form.save(commit=False)
        order.total = total
        order.save()
        for i in items:
            p = i["product"]
            OrderItem.objects.create(order=order, product=p, name=p.name, price=p.price,
                                     size=i["size"], color=i["color"], quantity=i["qty"])
            Product.objects.filter(pk=p.pk).update(stock=F("stock") - i["qty"])
    request.session["cart"] = {}
    request.session["last_order"] = order.pk
    return redirect("orders:confirmation", pk=order.pk)


def confirmation(request, pk):
    if request.session.get("last_order") != pk:
        return redirect("store:home")
    return render(request, "orders/confirmation.html", {"order": get_object_or_404(Order, pk=pk)})
