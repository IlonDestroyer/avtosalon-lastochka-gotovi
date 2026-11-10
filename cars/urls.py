from django.urls import path

from . import views

urlpatterns = [
    path("", views.CatalogView.as_view(), name="catalog"),
    path("cars/<slug:slug>/", views.CarDetailView.as_view(), name="car_detail"),
    path("cars/<slug:slug>/book/", views.create_booking, name="create_booking"),
    path("cars/<slug:slug>/testdrive/", views.create_testdrive, name="create_testdrive"),
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.UserLoginView.as_view(), name="login"),
    path("auth/logout/", views.UserLogoutView.as_view(), name="logout"),
    path("cabinet/", views.cabinet_view, name="cabinet"),
    path("payment/<int:booking_id>/", views.payment_view, name="payment"),
    path("support/", views.support_view, name="support"),
]
