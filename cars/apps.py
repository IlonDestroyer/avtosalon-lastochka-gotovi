from django.apps import AppConfig


class CarsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cars"
    verbose_name = "Автоцентр «Ласточка»"

    def ready(self):
        from . import signals  # noqa: F401
