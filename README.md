# Rosée — women's clothing shop (Django)

Girly pastel storefront + custom admin dashboard. Cash on delivery, prices in DZD.

## Run locally
```
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed                                  # sample data + admin / admin12345 (change it!)
python manage.py runserver
```
Shop: http://127.0.0.1:8000/ — Dashboard: http://127.0.0.1:8000/dashboard/

Own admin user instead of the seed one: `python manage.py createsuperuser`.
Rename the shop with `SHOP_NAME` in `.env`.

## Admin dashboard
- **Categories**: add (name + optional image), edit, delete. A category that still has products cannot be deleted; the dashboard tells you how many products block it.
- **Products**: category is required; name, description, price, sizes and colors (comma separated), stock, several photos, visible/hidden, show on homepage.
- **Orders**: Pending → Confirmed → Shipped → Delivered → Done (or Cancelled). Stock drops when an order is placed.

## Deploy on Vercel (+ Neon database + Cloudinary photos)
Vercel cannot keep a database file or uploaded photos, so the live site needs two free services:
**Neon** (PostgreSQL) and **Cloudinary** (product photos).

1. **Neon**: create a project, copy the connection string (`postgresql://...`).
2. **Cloudinary**: sign up, open the dashboard, copy the "API Environment variable" (`cloudinary://...`).
3. **Create the tables and sample products from your computer** (venv activated, `pip install -r requirements.txt` done), PowerShell:
   ```
   $env:DATABASE_URL="your-neon-string"
   $env:CLOUDINARY_URL="your-cloudinary-string"
   $env:DJANGO_SUPERUSER_USERNAME="your-admin-name"
   $env:DJANGO_SUPERUSER_PASSWORD="a-strong-password"
   python manage.py migrate
   python manage.py seed
   ```
4. **Generate a secret key**:
   `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
5. **Vercel -> Settings -> Environment Variables**, add exactly these three: `SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_URL`.
6. Push to GitHub (`git add . && git commit -m "deploy" && git push`). Vercel redeploys on its own.
7. Open your `.vercel.app` address; the admin is at `/dashboard/`.

If the site shows "Server Error (500)", open Vercel -> Logs; the error message says which variable is missing.

## Deploy elsewhere (Render, VPS)
Build: `pip install -r requirements.txt && python manage.py migrate` — Start: `gunicorn config.wsgi`.
Set `SECRET_KEY` and `DATABASE_URL` (and `CLOUDINARY_URL` for photos). Hosts and CSRF origins are set automatically on Render/Vercel.
