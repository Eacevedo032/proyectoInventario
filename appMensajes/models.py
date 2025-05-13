from django.db import models
from django.contrib.auth.models import User

#MODELO DE MENSAJES

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, related_name='mensajes_enviados', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    texto = models.TextField(blank=True)
    archivo = models.FileField(upload_to='mensajes/', blank=True, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False) # Indica si el mensaje ha sido leído o no

    def __str__(self):
        return f"De {self.remitente} para {self.destinatario} - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"
    
class ChatEliminado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    con_quien = models.ForeignKey(User, related_name='chats_eliminados', on_delete=models.CASCADE)
    fecha_eliminacion = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ('usuario', 'con_quien')