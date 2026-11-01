import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product

IMAGES = Path(__file__).resolve().parents[2] / "seed_images"
S, ONE, SHOES = "S,M,L,XL", "One size", "36,37,38,39,40"

# category -> [(name, price DZD, colors, sizes, stock, featured, description)]
DATA = {
    "Dresses": [
        ("Satin slip dress", 6900, "Blush,Lilac", S, 12, True, "A fluid satin dress with thin straps and a soft shine. Dress it up for evenings or down with a cardigan."),
        ("Floral midi dress", 7800, "Lilac,Peach", S, 9, True, "A flowy midi dress with a hand-drawn flower print. Light, cinched at the waist and perfect for spring."),
        ("Puff-sleeve mini dress", 6200, "Rose,Ivory", S, 3, True, "A playful mini dress with puffed sleeves and a ruffled hem. Soft cotton, easy to wear all day."),
    ],
    "Tops": [
        ("Ribbed bow top", 2900, "Ivory,Pink", S, 20, True, "A stretchy ribbed top with a little bow at the chest. Pairs with skirts, jeans and everything between."),
        ("Linen cropped shirt", 3400, "Lilac,Sand", S, 14, False, "A breathable linen shirt with a relaxed cropped cut. Keeps you cool and looks effortlessly put together."),
        ("Cream ribbed square-neck top", 3200, "Cream", S, 15, True, "A soft ribbed top with a square neckline, ruched front and flared sleeves. Fitted at the waist for a flattering shape."),
        ("Black draped cowl-neck top", 3500, "Black", S, 15, True, "An elegant black top with a draped cowl neckline and long flared sleeves. Stretchy, comfortable and easy to dress up."),
    ],
    "Pants": [
        ("Wide-leg denim jeans", 5200, "Light blue", S, 12, True, "High-waisted jeans with a relaxed wide leg and a classic light wash. Comfortable all day and easy to style."),
        ("Black wide-leg trousers", 4800, "Black", S, 12, False, "Smart high-waisted trousers with front pleats and a flowing wide leg. A modest, polished piece for work or outings."),
    ],
    "Skirts": [
        ("Pleated tulle skirt", 4500, "Blush,Lilac", S, 10, True, "A long, airy pleated skirt that moves with every step. Elastic waist for a comfortable fit."),
        ("Denim A-line skirt", 3900, "Blue,Light blue", S, 16, False, "A classic A-line denim skirt with contrast stitching. A wardrobe basic that goes with any top."),
        ("Black pleated midi skirt", 3800, "Black", S, 14, False, "A flowing black midi skirt with fine pleats and an elastic waist. Pairs easily with any top, day or evening."),
        ("Cream tiered midi skirt", 4200, "Cream", S, 10, True, "A soft cream skirt with three airy ruffled tiers and an elastic waist. Light, feminine and perfect with a fitted top."),
    ],
    "Hijabs": [
        ("Chiffon hijab", 1500, "Dusty rose,Lilac", ONE, 30, True, "A lightweight chiffon hijab that drapes softly and stays in place. Breathable and easy to style."),
        ("Black layered chiffon hijab", 1800, "Black", ONE, 25, False, "A layered black chiffon hijab with a soft drape. Light, breathable and stays neatly in place."),
        ("Beige layered chiffon hijab", 1800, "Beige", ONE, 25, True, "A layered beige chiffon hijab with a soft drape. Light, breathable and matches almost every outfit."),
    ],
    "Bags": [
        ("Cream shoulder bag", 4500, "Cream", ONE, 8, True, "A structured cream shoulder bag with gold details and a twist-lock closure. Roomy enough for your daily essentials."),
        ("Black quilted chain bag", 5500, "Black", ONE, 6, False, "A black quilted bag with a gold chain strap and a flap closure. A classic evening bag that goes with everything."),
    ],
    "Scarves": [
        ("Checked winter scarf", 2600, "Beige check", ONE, 18, False, "A warm, oversized scarf in a classic beige check with a fringed edge. Soft to the touch and ideal for cold days."),
        ("Burgundy winter scarf", 2200, "Burgundy", ONE, 18, True, "A soft, warm scarf in a deep burgundy with a fringed edge. Wrap it around your neck or drape it over your shoulders."),
    ],
    "Shoes": [
        ("Cream Mary Jane shoes", 5500, "Cream", SHOES, 10, True, "Cream Mary Jane shoes with a buckled strap and a low block heel. Comfortable to walk in and very feminine."),
        ("Black ballet flats", 4200, "Black", SHOES, 12, False, "Glossy black ballet flats with a little bow. Light, comfortable and easy to wear every day."),
    ],
    "Accessories": [
        ("Pearl hair clip set", 900, "Pearl", ONE, 25, True, "Four pearl hair clips in rose gold. A small detail that makes a simple hairstyle feel special."),
        ("Satin scrunchie trio", 700, "Pink,Lilac,Beige", ONE, 40, False, "Three silky scrunchies that are gentle on your hair. Wear them in a ponytail or around your wrist."),
    ],
}


class Command(BaseCommand):
    help = "Create sample categories, products with photos, and a default admin (admin / admin12345)."

    def handle(self, *args, **options):
        for cname, items in DATA.items():
            cat, _ = Category.objects.get_or_create(name=cname)
            for name, price, colors, sizes, stock, featured, desc in items:
                p, _ = Product.objects.update_or_create(category=cat, name=name, defaults={
                    "price": price, "colors": colors, "sizes": sizes, "stock": stock,
                    "is_featured": featured, "is_active": True, "description": desc})
                if not p.images.exists():
                    for f in sorted(IMAGES.glob(f"{slugify(name)}-*.jpg")):
                        with open(f, "rb") as fh:
                            img = p.images.model(product=p)
                            img.image.save(f.name, File(fh), save=True)
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            # Set DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD to choose your own (do this when deploying).
            user = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin12345")
            User.objects.create_superuser(user, "admin@example.com", password)
            self.stdout.write(f"Created admin user '{user}'." + (" Default password admin12345: change it!" if password == "admin12345" else ""))
        self.stdout.write(self.style.SUCCESS("Sample data ready."))
