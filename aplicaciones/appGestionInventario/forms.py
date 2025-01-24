from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

#Aca se llenaran los campos faltantes de User (de manera que es personalizado)
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Nombres")
    last_name = forms.CharField(max_length=50, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Dirección de correo electrónico")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    #Validación para que el usuario meta un nombre sin espacios, ya que django no lo permite
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if " " in username:
            raise ValidationError("El nombre de usuario no puede contener espacios.")
        return username