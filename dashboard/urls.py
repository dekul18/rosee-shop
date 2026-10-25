from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="dashboard/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.index, name="index"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("products/", views.products, name="products"),
    path("products/new/", views.product_form, name="product_new"),
    path("products/<int:pk>/edit/", views.product_form, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]
