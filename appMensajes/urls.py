from django.urls import path
from appMensajes import views

urlpatterns = [
path('listar_usuarios_chat/', views.listar_usuarios_chat, name='listar_usuarios_chat'), # Ruta para listar usuarios en el chat
path('chat_con_usuario/<int:usuario_id>/', views.chat_con_usuario, name='chat_con_usuario'), # Ruta para el chat con usuario
path('eliminar_conversacion/<int:usuario_id>/', views.eliminar_conversacion, name='eliminar_conversacion'), # Ruta para eliminar conversación
]