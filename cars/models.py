from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField("ФИО", max_length=200, blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.full_name or self.user.username


class Car(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_BOOKED = "booked"
    STATUS_SOLD = "sold"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "В наличии"),
        (STATUS_BOOKED, "Забронирован"),
        (STATUS_SOLD, "Продан"),
    ]

    slug = models.SlugField(max_length=200, unique=True, blank=True)
    brand = models.CharField("Марка", max_length=100)
    model = models.CharField("Модель", max_length=100)
    trim = models.CharField("Комплектация", max_length=100, blank=True)
    year = models.PositiveIntegerField("Год выпуска")
    body = models.CharField("Кузов", max_length=50, default="Седан")
    mileage_km = models.PositiveIntegerField("Пробег, км", default=0)
    fuel = models.CharField("Топливо", max_length=50, default="Бензин")
    horsepower = models.PositiveIntegerField("Мощность, л.с.", default=150)
    transmission = models.CharField("Коробка", max_length=50, default="Автомат")
    price_kzt = models.PositiveIntegerField("Цена, ₸")
    image = models.ImageField("Фото", upload_to="cars/", blank=True, null=True)
    image_url = models.URLField("Ссылка на фото", blank=True)
    description = models.TextField("Описание", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def title(self):
        parts = [self.brand, self.model, self.trim]
        return " ".join(p for p in parts if p)

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return ""

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.brand}-{self.model}-{self.trim}", allow_unicode=True)
            if not base:
                base = "car"
            self.slug = f"{base}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class Booking(models.Model):
    STATUS_CREATED = "created"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_CONFIRMED, "Подтверждена"),
        (STATUS_COMPLETED, "Завершена"),
        (STATUS_CANCELLED, "Отменена"),
        (STATUS_EXPIRED, "Просрочена"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )
    deposit_kzt = models.PositiveIntegerField("Предоплата, ₸", default=500_000)
    expires_at = models.DateTimeField("Действует до")
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Бронь {self.car} — {self.user}"

    def is_active(self):
        return self.status in (self.STATUS_CREATED, self.STATUS_CONFIRMED) and self.expires_at > timezone.now()


class TestDrive(models.Model):
    STATUS_PLANNED = "planned"
    STATUS_CONFIRMED = "confirmed"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Запланирован"),
        (STATUS_CONFIRMED, "Подтверждён"),
        (STATUS_DONE, "Проведён"),
        (STATUS_CANCELLED, "Отменён"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_drives",
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="test_drives")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )
    scheduled_at = models.DateTimeField("Дата и время")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тест-драйв"
        verbose_name_plural = "Тест-драйвы"
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Тест-драйв {self.car} — {self.scheduled_at:%d.%m.%Y %H:%M}"


class Payment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "В обработке"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_FAILED, "Не прошёл"),
    ]
    METHOD_CARD = "card"
    METHOD_TRANSFER = "transfer"
    METHOD_CHOICES = [
        (METHOD_CARD, "Карта"),
        (METHOD_TRANSFER, "Перевод"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="payments")
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    order_no = models.CharField("Номер заказа", max_length=50, unique=True)
    amount_kzt = models.PositiveIntegerField("Сумма, ₸")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default=METHOD_CARD,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_no} — {self.amount_kzt} ₸"

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
