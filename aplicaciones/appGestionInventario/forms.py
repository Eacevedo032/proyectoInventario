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
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Contraseña Actual"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Cambiar contraseña (Opcional)",
        help_text="Dejar en blanco si no desea cambiarla."
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirmar Contraseña"    
    )

    delete_picture = forms.BooleanField(
        required=False,
        label="Eliminar foto actual",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        labels = {
            'username': _('Nombre de Usuario'),
            'first_name': _('Nombres'),
            'last_name': _('Apellidos'),
            'email': _('Correo Institucional')
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Hacer opcionales
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        current_password = cleaned_data.get("current_password")

        # Si se intenta cambiar contraseña, verificar requisitos
        if password or confirm_password:
            if not current_password:
                self.add_error('current_password', "Debe ingresar su contraseña actual para cambiar la contraseña.")
            elif not self.user.check_password(current_password):
                self.add_error('current_password', "La contraseña actual no es correcta.")

            if password != confirm_password:
                self.add_error('confirm_password', "La nueva contraseña y su confirmación no coinciden.")
            else:
                # Validaciones de seguridad para contraseña
                if password and len(password) < 8:
                    self.add_error('password', "La nueva contraseña debe tener al menos 8 caracteres.")
                if password and not any(c.isdigit() for c in password):
                    self.add_error('password', "Debe contener al menos un número.")
                if password and not any(c.isalpha() for c in password):
                    self.add_error('password', "Debe contener al menos una letra.")
                if password == current_password:
                    self.add_error('password', "La nueva contraseña no puede ser igual a la actual.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        profile, created = UserProfile.objects.get_or_create(user=user)

        if self.cleaned_data.get('delete_picture'):
            profile.delete_profile_picture()

        if 'profile_picture' in self.files:
            if profile.profile_picture:
                profile.delete_profile_picture()
            profile.profile_picture = self.files['profile_picture']

        # Guardar nueva contraseña si se proporcionó
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)

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
