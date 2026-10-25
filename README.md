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

## Deploy (Render / Railway / VPS)
1. Create a PostgreSQL database and set `DATABASE_URL`.
2. Set `DEBUG=0`, a long random `SECRET_KEY`, `ALLOWED_HOSTS=yourdomain.com`, `CSRF_TRUSTED_ORIGINS=https://yourdomain.com`.
3. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. Start: `gunicorn config.wsgi`
5. Uploaded photos live in `media/`. Attach a persistent disk there, otherwise they disappear on redeploy (or move to S3/Cloudinary later).
