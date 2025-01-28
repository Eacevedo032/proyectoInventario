from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User #User propio de Django
from aplicaciones.appGestionInventario.forms import CustomUserCreationForm #Importa el formulario de registro de usuario personalizado de forms.py
from django.utils.safestring import mark_safe #Marca contenido seguro
from aplicaciones.appGestionInventario.models import ApprovedUser, DeniedUser #Tablas para guardar el historial de Usuarios denegados y aceptados
from django.contrib.auth import authenticate, login

# Vista para registrar un usuario nuevo 
def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desactiva el usuario por defecto
            user.save()
            messages.success(request, mark_safe(
                "Registro exitoso. Tu cuenta será activada tras la aprobación de un administrador. "
            ))
            return render(request, 'registration/register.html', {'form': CustomUserCreationForm()}) #Crea un nuevo formulario vacio cada vez que se desea registrar un nuevo usuario
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

"""
Vista `approve_users`

1. Obtiene tres listas principales:
   - Usuarios pendientes (`is_active=False`).
   - Usuarios aprobados (`is_active=True`).
   - Usuarios denegados (guardados en la sesión).

2. Maneja el formulario (POST):
   - `user_id`: ID del usuario enviado desde la plantilla.
   - `action`: Acción a realizar ('approve' o 'deny').

3. Acciones:
   - Aprobar: Activa al usuario (`is_active=True`) y lo guarda en la base de datos.
   - Denegar: Elimina al usuario de la base de datos y lo agrega a la lista de usuarios denegados.

4. Redirige a la misma página para actualizar la interfaz.
"""
# Vista para aprobar, denegar o eliminar usuarios
@login_required
def approve_users(request):
    pending_users = User.objects.filter(is_active=False)
    approved_users = ApprovedUser.objects.all()
    denied_users = DeniedUser.objects.all()

    if request.method == "POST":
        action = request.POST.get('action')  # Aprobar, Denegar, Eliminar o Limpiar historial
        user_id = request.POST.get('user_id')
        approved_user_id = request.POST.get('approved_user_id')

        if action == "approve":
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                ApprovedUser.objects.create(user=user, created_by=request.user)  # Guardar admin en created_by
                messages.success(request, f"Usuario {user.username} aprobado con éxito.")
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")
        
        elif action == "deny":
            try:
                user = User.objects.get(id=user_id)
                DeniedUser.objects.create(
                    username=user.username,
                    email=user.email,
                    created_by=request.user  # Guardar admin en created_by
                )
                user.delete()
                messages.success(request, f"Usuario {user.username} denegado y eliminado.")
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")
        
        elif action == "delete_approved":
            if approved_user_id:
                try:
                    approved_user = ApprovedUser.objects.get(id=approved_user_id)
                    approved_user.delete()
                    messages.success(request, "Registro del usuario aprobado eliminado con éxito.")
                except ApprovedUser.DoesNotExist:
                    messages.error(request, "El registro del usuario aprobado no existe.")
            else:
                messages.error(request, "ID de usuario aprobado no proporcionado.")

        elif action == "delete_approved_user":
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    ApprovedUser.objects.filter(user=user).delete()
                    user.delete()
                    messages.success(request, f"Usuario {user.username} eliminado con éxito.")
                except User.DoesNotExist:
                    messages.error(request, "El usuario no existe.")
            else:
                messages.error(request, "ID de usuario no proporcionado.")
        
        elif action == "delete_denied":
            try:
                denied_user = DeniedUser.objects.get(id=user_id)
                denied_user.delete()
                messages.success(request, f"Registro del usuario denegado eliminado con éxito.")
            except DeniedUser.DoesNotExist:
                messages.error(request, "El registro del usuario denegado no existe.")
        
        elif action == "clear_approved":
            try:
                ApprovedUser.objects.all().delete()
                messages.success(request, "Historial de usuarios aprobados limpiado con éxito.")
            except Exception as e:
                messages.error(request, f"Error al limpiar el historial de usuarios aprobados: {str(e)}")

        elif action == "clear_denied":
            try:
                DeniedUser.objects.all().delete()
                messages.success(request, "Historial de usuarios denegados limpiado con éxito.")
            except Exception as e:
                messages.error(request, f"Error al limpiar el historial de usuarios denegados: {str(e)}")

        return redirect('approve_users')

    # Renderizar la plantilla para solicitudes GET
    context = {
        'pending_users': pending_users,
        'approved_users': approved_users,
        'denied_users': denied_users,
    }
    return render(request, 'admin/approve_users.html', context)