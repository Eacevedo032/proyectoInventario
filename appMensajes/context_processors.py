# context_processors.py para que de la cantidad de mensajes no leídos para mostrarlo en un ícono en el base.html
from .models import Mensaje

def notificaciones_mensajes(request):
    if request.user.is_authenticated:
        no_leidos = Mensaje.objects.filter(destinatario=request.user, leido=False).count()
        return {'mensajes_no_leidos': no_leidos}
    return {}

'''
Este context processor se ejecuta en todas las plantillas renderizadas (si está activado en TEMPLATES en settings.py).

Calcula cuántos mensajes no leídos tiene el usuario autenticado.

Retorna ese conteo como una variable disponible en todas tus plantillas: mensajes_no_leidos.
'''