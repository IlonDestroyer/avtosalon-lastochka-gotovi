from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Booking, Car, Payment, Profile, TestDrive


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Профиль"


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "year",
        "body",
        "price_kzt",
        "status",
        "mileage_km",
        "created_at",
    )
    list_filter = ("status", "brand", "body", "year", "fuel", "transmission")
    search_fields = ("brand", "model", "trim", "slug", "description")
    list_editable = ("status",)
    prepopulated_fields = {"slug": ("brand", "model", "trim")}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": (
                "slug",
                "brand",
                "model",
                "trim",
                "year",
                "body",
                "status",
            )
        }),
        ("Характеристики", {
            "fields": (
                "mileage_km",
                "fuel",
                "horsepower",
                "transmission",
                "price_kzt",
            )
        }),
        ("Медиа и описание", {
            "fields": ("image", "image_url", "description")
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "car",
        "user",
        "status",
        "deposit_kzt",
        "expires_at",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "car__brand", "car__model")
    list_editable = ("status",)
    raw_id_fields = ("user", "car")
    readonly_fields = ("created_at",)


@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "user", "status", "scheduled_at", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "car__brand", "car__model")
    list_editable = ("status",)
    raw_id_fields = ("user", "car")
    readonly_fields = ("created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order_no",
        "car",
        "user",
        "amount_kzt",
        "status",
        "method",
        "created_at",
    )
    list_filter = ("status", "method")
    search_fields = ("order_no", "user__username", "user__email")
    list_editable = ("status",)
    raw_id_fields = ("user", "car", "booking")
    readonly_fields = ("order_no", "created_at")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone")
    search_fields = ("user__username", "user__email", "full_name", "phone")
