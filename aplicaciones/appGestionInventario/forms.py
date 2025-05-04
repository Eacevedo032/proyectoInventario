from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from aplicaciones.appGestionInventario.models import ApprovedUser 
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from aplicaciones.appGestionInventario.models import UserProfile

class EditProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        required=True,
        label="Contraseña Actual *",
        help_text="Requerida para confirmar cualquier cambio realizado en esta sección.",
        error_messages={
            'required': 'Debe ingresar su contraseña actual para realizar cambios'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        }), 
        required=False,
        label="Nueva Contraseña (Opcional)",
        help_text="Mínimo 8 caracteres con letras, números, signos. En caso de no desear actualizarla, dejar campo en blanco."
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off'
        }), 
        required=False,
        label="Confirmar Contraseña (Solo si se ingresó una nueva)",
        help_text="Sino se agregó una nueva contraseña, no confirmar."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tus nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tus apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
        }
        labels = {
            'username': _('Nombre de Usuario *'),
            'first_name': _('Nombres *'),
            'last_name': _('Apellidos *'),
            'email': _('Correo Electrónico *')
        }
        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio',
                'unique': 'Este nombre de usuario ya está en uso'
            }
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not current_password:
            raise ValidationError("Debe ingresar su contraseña actual")
            
        if not self.user.check_password(current_password):
            raise ValidationError("La contraseña actual no es correcta")
        return current_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("El nombre de usuario es obligatorio")
            
        # Verificar si el username cambió y si ya existe
        if username != self.instance.username and User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Ingrese un correo electrónico válido (ejemplo: usuario@dominio.com)")
        
        # Solo validar unicidad si el email cambió
        if email != self.instance.email and User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres")
            if not any(char.isdigit() for char in password):
                raise ValidationError("La contraseña debe contener al menos un número")
            if not any(char.isalpha() for char in password):
                raise ValidationError("La contraseña debe contener al menos una letra")
            if password == self.cleaned_data.get('current_password'):
                raise ValidationError("La nueva contraseña no puede ser igual a la actual")
        return password

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar coincidencia de contraseñas
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden")

        return cleaned_data
    
    delete_picture = forms.BooleanField(
        required=False,
        label="Eliminar foto actual",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Eliminar foto si se marcó el checkbox
        if self.cleaned_data.get('delete_picture'):
            profile.delete_profile_picture()
        
        # Actualizar foto si se subió una nueva
        if 'profile_picture' in self.files:
            # Eliminar la anterior si existe
            if profile.profile_picture:
                profile.delete_profile_picture()
            profile.profile_picture = self.files['profile_picture']
        
        if commit:
            user.save()
            profile.save()
        
        return user

#Form NUEVO para agregar un usuario por parte de un admin
#Se validan los nombres y correo, lo demás lo valida Django en su modelo de User

class CrearUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(max_length=50, required=False, label="Nombres")
    last_name = forms.CharField(max_length=50, required=False, label="Apellidos")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if " " in username:
            raise ValidationError("El nombre de usuario no puede contener espacios.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def save(self, commit=True, created_by=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
            if created_by:
                ApprovedUser.objects.create(user=user, created_by=created_by)
        return user
