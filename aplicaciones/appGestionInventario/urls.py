from django.urls import path, include
from aplicaciones.appGestionInventario.views import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView
from .views.Usuarios import edit_profile  # Importa la vista desde el archivo Usuarios.py para edición del perfil de usuario


urlpatterns = [
    path('inicioAplicacion', views.inicioAplicacion, name='inicioAplicacion'),

    path('', views.SISLAB, name='SISLAB'),

    path('SISLAB/', views.SISLAB, name='SISLAB'),

    #urls para las configuraciones de cuentas de usuario
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('editar-perfil/', views.edit_profile, name='editar_perfil'),  # Para editar el perfil
    #Agregar usuarios por parte de un admin NUEVO FINAL
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('gestion-usuarios/agregar/', views.agregar_usuario_admin, name='agregar_usuario_admin'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
