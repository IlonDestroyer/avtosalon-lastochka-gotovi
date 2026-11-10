from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .forms import (
    BookingForm,
    CarFilterForm,
    LoginForm,
    PaymentForm,
    RegisterForm,
    TestDriveForm,
)
from .models import Booking, Car, Payment, TestDrive


class CatalogView(ListView):
    model = Car
    template_name = "cars/catalog.html"
    context_object_name = "cars"
    paginate_by = 12

    def get_queryset(self):
        qs = Car.objects.all()
        form = self.get_filter_form()
        if form.is_valid():
            data = form.cleaned_data
            search = data.get("search")
            if search:
                qs = qs.filter(
                    Q(brand__icontains=search)
                    | Q(model__icontains=search)
                    | Q(trim__icontains=search)
                    | Q(body__icontains=search)
                    | Q(description__icontains=search)
                )
            brand = data.get("brand")
            if brand:
                qs = qs.filter(brand=brand)
            body = data.get("body")
            if body:
                qs = qs.filter(body=body)
            year = data.get("year")
            if year:
                qs = qs.filter(year=year)
            price_from = data.get("price_from")
            if price_from is not None:
                qs = qs.filter(price_kzt__gte=price_from * 1_000_000)
            price_to = data.get("price_to")
            if price_to is not None:
                qs = qs.filter(price_kzt__lte=price_to * 1_000_000)
        return qs

    def get_filter_form(self):
        brands = Car.objects.values_list("brand", flat=True).distinct().order_by("brand")
        years = Car.objects.values_list("year", flat=True).distinct().order_by("-year")
        return CarFilterForm(self.request.GET or None, brands=brands, years=years)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = self.get_filter_form()
        ctx["available_count"] = Car.objects.filter(status=Car.STATUS_AVAILABLE).count()
        return ctx


class CarDetailView(DetailView):
    model = Car
    template_name = "cars/car_detail.html"
    context_object_name = "car"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["booking_form"] = BookingForm()
        ctx["testdrive_form"] = TestDriveForm()
        return ctx


def register_view(request):
    if request.user.is_authenticated:
        return redirect("catalog")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна. Добро пожаловать!")
            return redirect("catalog")
    else:
        form = RegisterForm()
    return render(request, "cars/auth.html", {"form": form, "mode": "register"})


class UserLoginView(LoginView):
    template_name = "cars/auth.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "login"
        return ctx


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("catalog")


@login_required
def create_booking(request, slug):
    car = get_object_or_404(Car, slug=slug)
    if car.status != Car.STATUS_AVAILABLE:
        messages.error(request, "Этот автомобиль недоступен для бронирования.")
        return redirect("car_detail", slug=slug)

    if request.method != "POST":
        return redirect("car_detail", slug=slug)

    form = BookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Проверьте данные формы.")
        return redirect("car_detail", slug=slug)

    active = Booking.objects.filter(
        car=car,
        status__in=[Booking.STATUS_CREATED, Booking.STATUS_CONFIRMED],
        expires_at__gt=timezone.now(),
    ).exists()
    if active:
        messages.error(request, "Автомобиль уже забронирован.")
        return redirect("car_detail", slug=slug)

    booking = form.save(commit=False)
    booking.user = request.user
    booking.car = car
    booking.deposit_kzt = 500_000
    booking.expires_at = timezone.now() + timedelta(days=3)
    booking.status = Booking.STATUS_CREATED
    booking.save()

    car.status = Car.STATUS_BOOKED
    car.save(update_fields=["status"])

    messages.success(request, "Автомобиль забронирован на 3 дня.")
    return redirect("payment", booking_id=booking.pk)


@login_required
def create_testdrive(request, slug):
    car = get_object_or_404(Car, slug=slug)
    if car.status == Car.STATUS_SOLD:
        messages.error(request, "Нельзя записаться на тест-драйв проданного авто.")
        return redirect("car_detail", slug=slug)

    if request.method != "POST":
        return redirect("car_detail", slug=slug)

    form = TestDriveForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Укажите дату и время тест-драйва.")
        return redirect("car_detail", slug=slug)

    scheduled = form.cleaned_data["scheduled_at"]
    if scheduled <= timezone.now():
        messages.error(request, "Дата тест-драйва должна быть в будущем.")
        return redirect("car_detail", slug=slug)

    conflict = TestDrive.objects.filter(
        car=car,
        scheduled_at=scheduled,
        status__in=[TestDrive.STATUS_PLANNED, TestDrive.STATUS_CONFIRMED],
    ).exists()
    if conflict:
        messages.error(request, "Этот слот уже занят. Выберите другое время.")
        return redirect("car_detail", slug=slug)

    td = form.save(commit=False)
    td.user = request.user
    td.car = car
    td.status = TestDrive.STATUS_PLANNED
    td.save()

    messages.success(request, "Вы записаны на тест-драйв.")
    return redirect("cabinet")


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status == Booking.STATUS_COMPLETED:
        messages.info(request, "Эта бронь уже оплачена.")
        return redirect("cabinet")

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data["method"]
            payment = Payment.objects.create(
                user=request.user,
                car=booking.car,
                booking=booking,
                amount_kzt=booking.deposit_kzt,
                status=Payment.STATUS_PAID,
                method=method,
            )
            booking.status = Booking.STATUS_CONFIRMED
            booking.save(update_fields=["status"])
            messages.success(
                request,
                f"Оплата прошла успешно. Заказ {payment.order_no}.",
            )
            return redirect("cabinet")
    else:
        form = PaymentForm()

    return render(
        request,
        "cars/payment.html",
        {"booking": booking, "form": form},
    )


@login_required
def cabinet_view(request):
    profile = getattr(request.user, "profile", None)
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("car")
        .order_by("-created_at")
    )
    drives = (
        TestDrive.objects.filter(user=request.user)
        .select_related("car")
        .order_by("scheduled_at")
    )
    payments = (
        Payment.objects.filter(user=request.user)
        .select_related("car")
        .order_by("-created_at")
    )
    return render(
        request,
        "cars/cabinet.html",
        {
            "profile": profile,
            "bookings": bookings,
            "drives": drives,
            "payments": payments,
        },
    )


def support_view(request):
    return render(request, "cars/support.html")
