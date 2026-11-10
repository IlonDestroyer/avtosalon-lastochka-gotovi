from django import template

register = template.Library()


@register.filter
def format_kzt(value):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return value
    return f"{n:,}".replace(",", " ") + " ₸"


@register.filter
def format_number(value):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return value
    return f"{n:,}".replace(",", " ")
