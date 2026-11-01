from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from orders.models import Order
from store.models import Category, Product, ProductImage
from store.sample_data import load_samples, pending as pending_samples
from .forms import CategoryForm, ProductForm

LOW_STOCK = 5
staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="dashboard:login")


@staff_required
def index(request):
    valid = Order.objects.exclude(status=Order.CANCELLED)
    return render(request, "dashboard/index.html", {
        "orders_count": Order.objects.count(),
        "pending_count": Order.objects.filter(status=Order.PENDING).count(),
        "revenue": valid.aggregate(s=Sum("total"))["s"] or 0,
        "low_stock": Product.objects.filter(stock__lte=LOW_STOCK).select_related("category"),
        "recent": Order.objects.all()[:6], "low_limit": LOW_STOCK,
    })


@staff_required
def categories(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added.")
        return redirect("dashboard:categories")
    return render(request, "dashboard/categories.html", {
        "form": form, "categories": Category.objects.annotate(n=Count("products"))})


@staff_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=cat)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("dashboard:categories")
    return render(request, "dashboard/form.html", {"form": form, "title": f"Edit {cat.name}", "back": "dashboard:categories"})


@staff_required
@require_POST
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    try:
        cat.delete()
        messages.success(request, f"“{cat.name}” deleted.")
    except ProtectedError:
        n = cat.products.count()
        messages.error(request, f"“{cat.name}” still has {n} product(s). Move them to another category or delete them first.")
    return redirect("dashboard:categories")


@staff_required
def products(request):
    qs = Product.objects.select_related("category").prefetch_related("images")
    cat = request.GET.get("cat")
    if cat:
        qs = qs.filter(category_id=cat)
    return render(request, "dashboard/products.html", {
        "products": qs, "categories": Category.objects.all(), "cat": cat, "samples_missing": len(pending_samples())})


@staff_required
@require_POST
def import_samples(request):
    """Add the sample products straight from the dashboard (a few per click, so it stays under the host's time limit)."""
    try:
        created, left = load_samples(limit=4)
    except Exception as e:  # show the real reason (e.g. Cloudinary not configured) instead of a blank 500
        messages.error(request, f"Could not add the products: {type(e).__name__}: {e}")
        return redirect("dashboard:products")
    if created == 0:
        messages.success(request, "All sample products are already in your shop.")
    elif left:
        messages.success(request, f"{created} products added. {left} more to go — click the button again.")
    else:
        messages.success(request, f"{created} products added. All sample products are now in your shop.")
    return redirect("dashboard:products")


@staff_required
def product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    if not Category.objects.exists():
        messages.error(request, "Create a category first, then add products.")
        return redirect("dashboard:categories")
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        if product:
            p.images.filter(pk__in=request.POST.getlist("delete_images")).delete()
        for f in request.FILES.getlist("images"):
            ProductImage.objects.create(product=p, image=f)
        messages.success(request, "Product saved.")
        return redirect("dashboard:products")
    return render(request, "dashboard/product_form.html", {"form": form, "product": product})


@staff_required
@require_POST
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, "Product deleted.")
    return redirect("dashboard:products")


@staff_required
def orders(request):
    qs, status = Order.objects.all(), request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    return render(request, "dashboard/orders.html", {"orders": qs, "statuses": Order.STATUS, "status": status})


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    if request.method == "POST":
        new = request.POST.get("status")
        if new in dict(Order.STATUS):
            order.status = new
            order.save(update_fields=["status"])
            messages.success(request, f"Order #{order.pk} is now {order.get_status_display().lower()}.")
        return redirect("dashboard:order_detail", pk=pk)
    return render(request, "dashboard/order_detail.html", {"order": order, "statuses": Order.STATUS})


@staff_required
@require_POST
def order_status(request, pk):
    """Change an order's status from the drop-down (works with fetch and as a plain form post)."""
    order = get_object_or_404(Order, pk=pk)
    new = request.POST.get("status")
    ok = new in dict(Order.STATUS)
    if ok:
        order.status = new
        order.save(update_fields=["status"])
    if request.headers.get("X-Requested-With") == "fetch":
        return JsonResponse({"ok": ok, "status": order.status, "label": order.get_status_display()}, status=200 if ok else 400)
    if ok:
        messages.success(request, f"Order #{order.pk} is now {order.get_status_display().lower()}.")
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("dashboard:orders")
