from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Profile, TestDrive


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    full_name = forms.CharField(max_length=200, required=False, label="ФИО")
    phone = forms.CharField(max_length=30, required=False, label="Телефон")

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": self.cleaned_data.get("full_name", ""),
                    "phone": self.cleaned_data.get("phone", ""),
                },
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("comment",)
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Комментарий менеджеру (необязательно)",
                    "class": "form-control",
                }
            ),
        }
        labels = {"comment": ""}


class TestDriveForm(forms.ModelForm):
    class Meta:
        model = TestDrive
        fields = ("scheduled_at",)
        widgets = {
            "scheduled_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        labels = {"scheduled_at": "Дата и время тест-драйва"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scheduled_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class PaymentForm(forms.Form):
    method = forms.ChoiceField(
        choices=[("card", "Банковская карта"), ("transfer", "Банковский перевод")],
        widget=forms.RadioSelect,
        label="Способ оплаты",
        initial="card",
    )


class CarFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(attrs={"placeholder": "BMW X5, 2023, седан"}),
    )
    brand = forms.ChoiceField(required=False, label="Марка")
    body = forms.ChoiceField(
        required=False,
        label="Кузов",
        choices=[("", "Все"), ("Седан", "Седан"), ("Кроссовер", "Кроссовер")],
    )
    year = forms.ChoiceField(required=False, label="Год")
    price_from = forms.IntegerField(
        required=False,
        label="Цена от, млн ₸",
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "от 8"}),
    )
    price_to = forms.IntegerField(
        required=False,
        label="Цена до, млн ₸",
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "до 60"}),
    )

    def __init__(self, *args, brands=None, years=None, **kwargs):
        super().__init__(*args, **kwargs)
        brand_choices = [("", "Все марки")]
        if brands:
            brand_choices += [(b, b) for b in brands]
        self.fields["brand"].choices = brand_choices

        year_choices = [("", "Любой")]
        if years:
            year_choices += [(str(y), str(y)) for y in years]
        self.fields["year"].choices = year_choices
