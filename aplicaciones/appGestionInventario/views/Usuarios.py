from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User #User propio de Django
from aplicaciones.appGestionInventario.forms import CustomUserCreationForm #Importa el formulario de registro de usuario personalizado de forms.py
from django.utils.safestring import mark_safe #Marca contenido seguro
from aplicaciones.appGestionInventario.models import ApprovedUser #Tablas para guardar el historial de Usuarios aceptados
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView

# Vista para registrar un usuario nuevo 
def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desactiva el usuario por defecto
            user.save()
            messages.success(request, mark_safe(
                "Registro exitoso. Tu cuenta será activada o eliminada tras la verificación de un administrador. "
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
    pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
    approved_users = ApprovedUser.objects.all().order_by('-date_approved')

    if request.method == "POST":
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        approved_user_id = request.POST.get('approved_user_id')

        if action == "approve":
            try:
                user = User.objects.get(id=user_id)
                if not ApprovedUser.objects.filter(user=user).exists():
                    user.is_active = True
                    user.save()
                    ApprovedUser.objects.create(user=user, created_by=request.user)
                    messages.success(request, f"Usuario {user.username} aprobado (activado) con éxito.")
                else:
                    messages.warning(request, "Este usuario ya ha sido aprobado previamente.")
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")

        elif action == "toggle_superuser":
            try:
                user = User.objects.get(id=user_id)

                if user.is_superuser:
                    # Quitar privilegios de superusuario
                    user.is_superuser = False
                    user.is_staff = False
                    user.is_active = True  # Sigue siendo activo como usuario normal
                    messages.success(request, f"El usuario {user.username} ahora es un usuario común.")
                else:
                    # Promover a superusuario
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    messages.success(request, f"El usuario {user.username} ha sido promovido a administrador.")

                user.save()
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")

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

        return redirect('approve_users')

    context = {
        'pending_users': pending_users,
        'approved_users': approved_users
    }
    return render(request, 'admin/approve_users.html', context)


#Validación de que el usuario ingresado exista, se ingrese correctamente, pendiente o denegado.
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')  # Se obtiene directamente con un POST
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Debe ingresar un usuario y una contraseña.")
            return redirect('login')

        # Buscamos en User si existe con ese username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "El usuario ingresado no existe.")
            return redirect('login')

        # Verificamos si el usuario existe pero está INACTIVO
        if not user.is_active:
            messages.warning(request, "Su cuenta está pendiente de aprobación por parte del administrador.")
            return redirect('login')

        # Intentamos autenticarlo con la contraseña
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}.")
            return redirect('inicio')  # Lo dirigimos ya logueado al inicio
        else:
            messages.error(request, "Usuario o contraseña no coinciden. Ingréselos correctamente.")
            return redirect('login')


from aplicaciones.appGestionInventario.forms import EditProfileForm

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('editar_perfil')
    else:
        form = EditProfileForm(instance=request.user, user=request.user)

    return render(request, "editar_perfil.html", {
        "form": form,
        "user": request.user
    })