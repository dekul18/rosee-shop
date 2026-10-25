from django.shortcuts import render
from .models import Category, Product


def _payload(products):
    """Data the product popup needs; rendered once as JSON, no extra requests."""
    return [{
        "id": p.id, "name": p.name, "price": f"{p.price:,.0f}", "desc": p.description,
        "cat": p.category.slug, "catName": p.category.name,
        "images": [i.image.url for i in p.images.all()],
        "sizes": p.size_list, "colors": p.color_list, "stock": p.stock,
    } for p in products]


def _products():
    return Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")


def home(request):
    products = list(_products())
    featured = [p for p in products if p.is_featured][:8] or products[:8]
    return render(request, "store/home.html", {
        "categories": Category.objects.all(),
        "products": featured,
        "products_json": _payload(featured),
    })


def shop(request):
    products = _products()
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(name__icontains=q)
    products = list(products)
    return render(request, "store/shop.html", {
        "categories": Category.objects.all(),
        "products": products, "q": q,
        "products_json": _payload(products),
        "active_cat": request.GET.get("cat", ""),
    })
