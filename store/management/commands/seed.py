import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from store.sample_data import load_samples


class Command(BaseCommand):
    help = "Add the sample categories/products with photos (existing products are left alone) and a default admin if none exists."

    def handle(self, *args, **options):
        created, _ = load_samples()
        self.stdout.write(f"{created} new product(s) added.")
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            # Set DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD to choose your own (do this when deploying).
            user = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin12345")
            User.objects.create_superuser(user, "admin@example.com", password)
            self.stdout.write(f"Created admin user '{user}'." + (" Default password admin12345: change it!" if password == "admin12345" else ""))
        self.stdout.write(self.style.SUCCESS("Sample data ready."))
