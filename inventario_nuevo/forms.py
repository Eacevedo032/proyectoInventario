from django import forms
from .models import Producto
from .models import Categoria, Subcategoria
from .models import Marca, Modelo, Color
from django.forms import DateInput
from django.core.exceptions import ValidationError
from .models import Presentacion, Capacidad, Accesorios
from .models import Ubicacion, Lote, Medida, EstadoRecurso, UnidadMedida

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['fecha_agregado']  # Excluirlo del formulario
        widgets = {
            'vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'num_cat': forms.TextInput(attrs={'class': 'form-control'}),
            'num_serie': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración inicial de campos
        self.set_required_fields()
        self.set_optional_fields()
        self.apply_bootstrap_classes()
        self.setup_category_filtering()
        self.order_choices_for_ux()

        # Asegurar IDs específicos para los selects
        self.fields['categoria'].widget.attrs.update({'id': 'id_categoria'})
        self.fields['subcategoria'].widget.attrs.update({'id': 'id_subcategoria'})

    def set_required_fields(self):
        required_fields = [
            'nombre', 'cantidad_disponible', 'unidad_medida',
            'categoria', 'subcategoria', 'estado', 'agregado_por',
        ]
        for field in required_fields:
            self.fields[field].required = True

    def set_optional_fields(self):
        optional_fields = [
            'lote', 'marca', 'modelo', 'color', 'presentacion',
            'capacidad', 'accesorios', 'medida', 'ubicacion',
            'codigo', 'num_cat', 'num_serie', 'vencimiento'
        ]
        for field in optional_fields:
            self.fields[field].required = False

    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

    def setup_category_filtering(self):
        """El queryset de subcategoría vacío, se cargará por AJAX."""
        self.fields['subcategoria'].queryset = Subcategoria.objects.none()

    def order_choices_for_ux(self):
        """Acá se ordena opciones para mejor experiencia de usuario"""
        if hasattr(self.fields['categoria'], 'queryset'):
            self.fields['categoria'].queryset = self.fields['categoria'].queryset.order_by('nombre')

        if hasattr(self.fields['unidad_medida'], 'queryset'):
            self.fields['unidad_medida'].queryset = self.fields['unidad_medida'].queryset.order_by('nombre')

#Gestionar categoría y subcategorías por medio de un form para la vista de catálogos de categoría que manda a llamar a la subcategoría asociada
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        qs = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"Ya existe una categoría con el nombre '{nombre}'.")
        return nombre

class SubcategoriaForm(forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['categoria', 'nombre', 'descripcion']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise ValidationError("El nombre de la subcategoría es obligatorio.")
        qs = Subcategoria.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"Ya existe una subcategoría con el nombre '{nombre}'.")
        return nombre

#Form de Marca, modelo, y color para catálogo
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre', 'codigo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre de la marca no puede estar vacío.")
        elif Marca.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una marca con ese nombre.")
        return nombre

class ModeloForm(forms.ModelForm): 
    class Meta:
        model = Modelo
        fields = ['nombre', 'codigo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modificar las etiquetas de los campos
        self.fields['nombre'].label = 'Nombre (requerido)'
        self.fields['codigo'].label = 'Código (opcional)'
        self.fields['descripcion'].label = 'Descripción (opcional)'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del modelo no puede estar vacío.")
        elif Modelo.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe un modelo con ese nombre.")
        return nombre

#El FORM PARA EL COLOR
class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['codigo', 'nombre', 'descripcion']
        labels = {
            'codigo': 'Código de Color',
            'nombre': 'Nombre',
            'descripcion': 'Descripción'
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del color no puede estar vacío.")
        elif Color.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe un color con ese nombre.")
        return nombre
    
# Formulario para Presentación
class PresentacionForm(forms.ModelForm):
    class Meta:
        model = Presentacion
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre (requerido)',
            'descripcion': 'Descripción (opcional)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la presentación no puede estar vacío.")
        elif Presentacion.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una presentación con ese nombre.")
        return nombre


# Formulario para Capacidad
class CapacidadForm(forms.ModelForm):
    class Meta:
        model = Capacidad
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre (requerido)',
            'descripcion': 'Descripción (opcional)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la capacidad no puede estar vacío.")
        elif Capacidad.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una capacidad con ese nombre.")
        return nombre


# Formulario para Accesorios
class AccesoriosForm(forms.ModelForm):
    class Meta:
        model = Accesorios
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre (requerido)',
            'descripcion': 'Descripción (opcional)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del accesorio no puede estar vacío.")
        elif Accesorios.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe un accesorio con ese nombre.")
        return nombre
    
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['codigo', 'nombre', 'descripcion']
        labels = {
            'codigo': 'Código de Ubicación',
            'nombre': 'Nombre',
            'descripcion': 'Descripción'
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la ubicación no puede estar vacío.")
        elif Ubicacion.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una ubicación con ese nombre.")
        return nombre
    
#Form de Lote
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['codigo', 'descripcion', 'fecha_vencimiento']
        labels = {
            'codigo': 'Código de Lote',
            'descripcion': 'Descripción',
            'fecha_vencimiento': 'Fecha de Vencimiento'
        }
        widgets = {
        'codigo': forms.TextInput(attrs={'class': 'form-control'}),
        'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'fecha_vencimiento': forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
            }),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo', '').strip()
        if not codigo:
            raise forms.ValidationError("El código del lote no puede estar vacío.")
        elif Lote.objects.filter(codigo__iexact=codigo).exists():
            raise forms.ValidationError("Ya existe un lote con ese código.")
        return codigo

#Form de las medidas de los Productos
class MedidaForm(forms.ModelForm):
    class Meta:
        model = Medida
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Medida',
            'descripcion': 'Descripción'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("La medida no puede estar vacía.")
        elif Medida.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una medida con ese valor.")
        return nombre
    
class EstadoRecursoForm(forms.ModelForm):
    class Meta:
        model = EstadoRecurso
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ['nombre', 'abreviatura', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'abreviatura': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }