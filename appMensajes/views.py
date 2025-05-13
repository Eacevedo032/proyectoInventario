from django.shortcuts import render, redirect, get_object_or_404
from appMensajes.models import Mensaje, ChatEliminado
from appMensajes.forms import MensajeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone

User = get_user_model()

#En el listado de usuarios se ve si tiene algun mensaje no leído utilizando el no_leidos, el campo leido en BD
#El context processors con la vista de notificaciones, que a su vez ocupa el modelo Mensaje.

@login_required
def listar_usuarios_chat(request):
    usuarios = User.objects.exclude(id=request.user.id).filter(is_active=True)
    
    conversaciones_activas = []
    
    for usuario in usuarios:
        eliminacion = ChatEliminado.objects.filter(
            usuario=request.user,
            con_quien=usuario
        ).first()
        
        mensajes_query = Mensaje.objects.filter(
            Q(remitente=usuario, destinatario=request.user) |
            Q(remitente=request.user, destinatario=usuario)
        )
        
        if eliminacion:
            mensajes_query = mensajes_query.filter(fecha_envio__gte=eliminacion.fecha_eliminacion)
        
        tiene_mensajes = mensajes_query.exists()
        no_leidos = Mensaje.objects.filter(
            remitente=usuario,
            destinatario=request.user,
            leido=False
        )
        
        if eliminacion:
            no_leidos = no_leidos.filter(fecha_envio__gte=eliminacion.fecha_eliminacion)
        
        no_leidos = no_leidos.count()
        
        if tiene_mensajes:
            conversaciones_activas.append({
                'usuario': usuario,
                'no_leidos': no_leidos,
                'es_reconexion': eliminacion is not None
            })
    
    return render(request, 'listar_usuarios.html', {
        'usuarios_info': usuarios,
        'conversaciones_activas': conversaciones_activas,
    })

@login_required
def eliminar_conversacion(request, usuario_id):
    usuario_destino = get_object_or_404(User, pk=usuario_id)
    
    ChatEliminado.objects.update_or_create(
        usuario=request.user,
        con_quien=usuario_destino,
        defaults={'fecha_eliminacion': timezone.now()}
    )
    
    messages.success(request, 'La conversación ha sido eliminada.')
    return redirect('listar_usuarios_chat')

@login_required
def chat_con_usuario(request, usuario_id):
    usuario_destino = get_object_or_404(User, pk=usuario_id)
    
    # Marcar mensajes como leídos
    Mensaje.objects.filter(
        remitente=usuario_destino,
        destinatario=request.user,
        leido=False
    ).update(leido=True)
    
    eliminacion = ChatEliminado.objects.filter(
        usuario=request.user,
        con_quien=usuario_destino
    ).first()
    
    mensajes = Mensaje.objects.filter(
        Q(remitente=request.user, destinatario=usuario_destino) |
        Q(remitente=usuario_destino, destinatario=request.user)
    )
    
    if eliminacion:
        mensajes = mensajes.filter(fecha_envio__gte=eliminacion.fecha_eliminacion)
    
    mensajes = mensajes.order_by('fecha_envio')

    usuarios_info = User.objects.exclude(id=request.user.id).filter(is_active=True)
    
    if request.method == 'POST':
        form = MensajeForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_mensaje = form.save(commit=False)
            nuevo_mensaje.remitente = request.user
            nuevo_mensaje.destinatario = usuario_destino
            nuevo_mensaje.save()
            messages.success(request, 'Mensaje enviado con éxito.')
            return redirect('chat_con_usuario', usuario_id=usuario_id)
    else:
        form = MensajeForm()

    return render(request, 'chat_con_usuario.html', {
        'mensajes': mensajes,
        'form': form,
        'usuario_destino': usuario_destino,
        'usuarios_info': usuarios_info,
    })