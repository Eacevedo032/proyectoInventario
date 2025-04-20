# inventarioNuevo/templatetags/form_filters.py
from django.forms.boundfield import BoundField
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css_class})
    return field  # En caso de que no sea un campo de formulario, simplemente devuelve el valor

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, [])