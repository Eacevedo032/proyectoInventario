from django import template
from django.forms.boundfield import BoundField

register = template.Library()

#El add_class se ocupa en la plantilla de register.html, siempre debe estar en la carpeta templatetags
#a nivel de las views, models, urls en la app, y debe ir acompañado de un __init__.py aunque sea vacio
#Además, este se carga con el load custom_... arriba de cada plantilla que lo use. 

#add_class: Este filtro generalmente se define para modificar los atributos de un widget HTML de un 
#campo de formulario.

#field.as_widget(attrs={"class": css_class}): Genera el campo HTML como si fuera un widget e inyecta 
#la clase css_class en su atributo class.

from django.forms.utils import flatatt
from django.utils.html import format_html

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css_class})
    return field  # Si no es un campo de formulario, simplemente lo devuelve sin cambios

@register.filter
def attr(field, attributes_str):
    """
    Filtro para agregar múltiples atributos a un campo de formulario.
    Debe aplicarse DESPUÉS de cualquier filtro que modifique el campo.
    """
    if hasattr(field, 'as_widget'):
        attrs = {}
        parts = [part.strip() for part in attributes_str.split(',')]
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                attrs[key.strip()] = value.strip()
        return field.as_widget(attrs=attrs)
    return field
