from django.conf import settings


def shop(request):
    cart = request.session.get("cart", {})
    return {"SHOP_NAME": settings.SHOP_NAME, "cart_count": sum(cart.values())}
