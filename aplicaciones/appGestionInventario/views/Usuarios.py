from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User #User propio de Django
from aplicaciones.appGestionInventario.forms import CrearUsuarioForm #Importa a Forms.py
from aplicaciones.appGestionInventario.models import ApprovedUser 
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from aplicaciones.appGestionInventario.forms import EditProfileForm #Importa a Forms.py
from django.contrib.auth import update_session_auth_hash # Para mantener la sesión activa después de cambiar la contraseña

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

        # Intentamos autenticarlo con la contraseña
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}.")
            return redirect('inicioAplicacion')  # Lo dirigimos ya logueado al inicio de la app
        else:
            messages.error(request, "Usuario o contraseña no coinciden. Ingréselos correctamente.")
            return redirect('login')

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
        
        if form.is_valid():
            user = form.save()

            # Mantener la sesión si se cambió la contraseña
            if form.cleaned_data.get('password'):
                update_session_auth_hash(request, user)

            if form.cleaned_data.get('delete_picture'):
                messages.success(request, "Foto de perfil eliminada correctamente.")
            else:
                messages.success(request, "Perfil actualizado correctamente.")

            return redirect('editar_perfil')
    else:
        form = EditProfileForm(instance=request.user, user=request.user)

    return render(request, "editar_perfil.html", {
        "form": form,
        "user": request.user
    })

# Vista para gestionar usuarios por parte de un administrador NUEVO FINAL

# Solo accesible por superusuarios
def solo_superusuarios(user):
    return user.is_superuser

#Vista para pagina y listar usuarios agregados por el admin
from aplicaciones.appGestionInventario.models import UserProfile  

@login_required
@user_passes_test(solo_superusuarios)
def gestion_usuarios(request):
    if request.method == "POST":
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action and user_id:
            try:
                user = User.objects.get(id=user_id)

                # Verificar que no se elimine o cambie el rol de un admin
                if user == request.user:
                    messages.error(request, "No puedes eliminarte a ti mismo ni cambiar tu propio rol.")
                    return redirect('gestion_usuarios')

                if user.is_superuser and action == "delete_user":
                    messages.error(request, "No puedes eliminar a un usuario administrador.")
                    return redirect('gestion_usuarios')

                if action == "delete_user":
                    ApprovedUser.objects.filter(user=user).delete()
                    user.delete()
                    messages.success(request, f"Usuario {user.username} eliminado con éxito.")

                elif action == "toggle_superuser":
                    if user.is_superuser:
                        user.is_superuser = False
                        messages.success(request, f"El usuario {user.username} ahora es un usuario común.")
                    else:
                        user.is_superuser = True
                        messages.success(request, f"El usuario {user.username} ha sido promovido a administrador.")
                    user.save()

            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")

        return redirect('gestion_usuarios')

    usuarios_list = User.objects.all().order_by('-date_joined')

    # Perfil de usuario
    for u in usuarios_list:
        u.profile = getattr(u, 'userprofile', None)

    paginator = Paginator(usuarios_list, 3)  # 3 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/gestion_usuarios.html', {
        'page_obj': page_obj,
    })

@login_required
@user_passes_test(solo_superusuarios)
def agregar_usuario_admin(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            form.save(created_by=request.user)
            messages.success(request, "Usuario creado y activado exitosamente.")
            return redirect('gestion_usuarios')
    else:
        form = CrearUsuarioForm()
    
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/agregar_usuario_admin.html', {'form': form, 'usuarios': usuarios})