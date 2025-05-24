#Formulario para el mensaje
from django import forms
from .models import Mensaje
from django.core.exceptions import ValidationError

'''
Está ligado al modelo Mensaje, por eso hereda de ModelForm.

Solo incluye los campos texto y archivo del modelo.

Personaliza el campo texto con un textarea pequeño.

Agrega una validación personalizada en clean_archivo:

Si se adjunta un archivo mayor a 10 MB, lanza un ValidationError.
'''


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['texto', 'archivo']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escribe un mensaje...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto')
        archivo = self.files.get('archivo')  # <- usar self.files para evitar lanzar ese error cuando en realidad sí hay contenido pero el archivo es inválido por su tamaño.

        # Solo validar si está completamente vacío y no hay archivo
        if not texto and not archivo:
         raise ValidationError("No puedes enviar un mensaje vacío.")

        return cleaned_data

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if archivo.size > 20 * 1024 * 1024:  # 10 MB
                raise ValidationError("El archivo no puede superar los 20 MB.")
        return archivo
