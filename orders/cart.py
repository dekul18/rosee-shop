from store.models import Product


def cart_items(request):
    """Return (items, total) for the session cart. Keys look like 'productId|size|color'."""
    cart = request.session.get("cart", {})
    ids = {int(k.split("|")[0]) for k in cart}
    products = Product.objects.filter(pk__in=ids, is_active=True).prefetch_related("images").in_bulk()
    items, total = [], 0
    for key, qty in cart.items():
        pid, size, color = key.split("|")
        p = products.get(int(pid))
        if not p:
            continue
        subtotal = p.price * qty
        total += subtotal
        items.append({"key": key, "product": p, "size": size, "color": color, "qty": qty, "subtotal": subtotal})
    return items, total
