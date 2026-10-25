from django import forms
from store.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "image"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "description", "price", "sizes", "colors", "stock", "is_active", "is_featured"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
