# Автоцентр «Ласточка» — Django

Классический Django-проект: каталог, бронирование, тест-драйвы, личный кабинет, Django Admin.

## Локальный запуск

```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_cars
python manage.py runserver
```

- Сайт: http://127.0.0.1:8000/
- Админка: http://127.0.0.1:8000/admin/ (admin / admin после seed_cars)

## Деплой на Render

1. Загрузите проект на **GitHub** (новый репозиторий).
2. На [render.com](https://render.com) создайте **PostgreSQL** (Free).
3. Создайте **Web Service** → Connect репозиторий:
   - **Runtime:** Python 3
   - **Build Command:** `chmod +x build.sh && ./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
4. Environment Variables:
   - `SECRET_KEY` — любая длинная случайная строка
   - `DEBUG` = `False`
   - `DATABASE_URL` — скопируйте **Internal Database URL** из PostgreSQL-сервиса
   - `PYTHON_VERSION` = `3.12.0` (по желанию)
5. После деплоя откройте Shell в Render и выполните:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_cars
   ```

Сайт будет на адресе вида `https://your-app.onrender.com`.
