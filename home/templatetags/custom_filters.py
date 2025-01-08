from django import template

register = template.Library()


@register.filter
def get_first_letter(username):
    return username[0] if username else '?'