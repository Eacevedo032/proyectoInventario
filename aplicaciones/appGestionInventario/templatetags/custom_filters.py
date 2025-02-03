from django import template

register = template.Library()

#El add_class se ocupa en la plantilla de register.html, siempre debe estar en la carpeta templatetags
#a nivel de las views, models, urls en la app, y debe ir acompañado de un __init__.py aunque sea vacio
#Además, este se carga con el load custom_... arriba de cada plantilla que lo use. 

#add_class: Este filtro generalmente se define para modificar los atributos de un widget HTML de un 
#campo de formulario.

#field.as_widget(attrs={"class": css_class}): Genera el campo HTML como si fuera un widget e inyecta 
#la clase css_class en su atributo class.

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
