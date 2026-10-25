from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "category"
            slug, n = base, 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    # PROTECT: a category that still has products cannot be deleted by accident.
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sizes = models.CharField(max_length=120, default="S,M,L,XL", help_text="Comma separated, e.g. XS,S,M,L,XL,XXL")
    colors = models.CharField(max_length=200, blank=True, help_text="Comma separated, e.g. Blush,Ivory,Black")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Visible in shop", default=True)
    is_featured = models.BooleanField("Show on homepage", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def _split(value):
        return [v.strip() for v in value.split(",") if v.strip()]

    @property
    def size_list(self):
        return self._split(self.sizes)

    @property
    def color_list(self):
        return self._split(self.colors)

    @property
    def main_image(self):
        img = self.images.first()
        return img.image.url if img else ""

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")

    class Meta:
        ordering = ["id"]
