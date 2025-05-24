from django import forms
from .models import Producto
from .models import Categoria, Subcategoria
from .models import Marca, Modelo, Color
from django.forms import DateInput
from django.core.exceptions import ValidationError
from .models import Presentacion, Capacidad, Accesorios
from .models import Ubicacion, Lote, Medida, EstadoRecurso, UnidadMedida

from django.core.exceptions import ValidationError
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['fecha_agregado']
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

        self.set_required_fields()
        self.set_optional_fields()

         # Filtrar para solo mostrar "disponible"
        estado_disponible = EstadoRecurso.objects.filter(estado='disponible').first()
        self.fields['estado'].queryset = EstadoRecurso.objects.filter(pk=estado_disponible.pk)

        # Mostrar como campo deshabilitado
        self.fields['estado'].initial = estado_disponible
        self.fields['estado'].disabled = True  # Se muestra, pero no editable

        self.apply_bootstrap_classes()
        self.setup_category_filtering()
        self.order_choices_for_ux()

        self.fields['categoria'].widget.attrs.update({'id': 'id_categoria'})
        self.fields['subcategoria'].widget.attrs.update({'id': 'id_subcategoria'})
        self.fields['cantidad_disponible'].label = "Cantidad"

    def set_required_fields(self):
        required_fields = [
            'nombre', 'cantidad_disponible', 'unidad_medida',
            'categoria', 'subcategoria', 'estado', 'agregado_por', 'ubicacion'
        ]
        for field in required_fields:
            self.fields[field].required = True

    def set_optional_fields(self):
        optional_fields = [
            'lote', 'marca', 'modelo', 'color', 'presentacion',
            'capacidad', 'accesorios', 'medida',
            'codigo', 'num_cat', 'num_serie', 'vencimiento'
        ]
        for field in optional_fields:
            self.fields[field].required = False

    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

    def setup_category_filtering(self):
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['subcategoria'].queryset = Subcategoria.objects.none()
        elif self.instance.pk and self.instance.categoria:
            self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria=self.instance.categoria).order_by('nombre')
        else:
            self.fields['subcategoria'].queryset = Subcategoria.objects.none()


    def order_choices_for_ux(self):
        if hasattr(self.fields['categoria'], 'queryset'):
            self.fields['categoria'].queryset = self.fields['categoria'].queryset.order_by('nombre')
        if hasattr(self.fields['unidad_medida'], 'queryset'):
            self.fields['unidad_medida'].queryset = self.fields['unidad_medida'].queryset.order_by('nombre')

    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data.get('cantidad_disponible')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad

    #  Aquí añadimos la validación de campos únicos
    def clean(self):
        cleaned_data = super().clean()
        codigo = cleaned_data.get('codigo')
        num_cat = cleaned_data.get('num_cat')
        num_serie = cleaned_data.get('num_serie')

        # Importante: excluir el producto actual en edición
        qs = Producto.objects.all()
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if codigo and qs.filter(codigo=codigo).exists():
            self.add_error('codigo', 'Este código ya está en uso.')

        if num_cat and qs.filter(num_cat=num_cat).exists():
            self.add_error('num_cat', 'Este número de catálogo ya existe.')

        if num_serie and qs.filter(num_serie=num_serie).exists():
            self.add_error('num_serie', 'Este número de serie ya está registrado.')


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
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
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
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modificar las etiquetas de los campos
        self.fields['nombre'].label = 'Nombre (requerido)'
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
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción'
        }
        widgets = {
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
        fields = ['nombre', 'descripcion'] 
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción'
        }
        widgets = {
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
        fields = ['nombre', 'descripcion', 'fecha_vencimiento']
        labels = {
            'nombre': 'Nombre del Lote',
            'descripcion': 'Descripción',
            'fecha_vencimiento': 'Fecha de Vencimiento'
        }
        widgets = {
        'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'fecha_vencimiento': forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del lote no puede estar vacío.")
        elif Lote.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe un lote con ese nombre.")
        return nombre

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

#Formulario de Editar Product
class ProductoEditForm(forms.ModelForm):
    cantidad_disponible = forms.DecimalField(
        label="Cantidad Disponible",
        min_value=0,  # No negativo
        decimal_places=2,  # Decimales permitidos
        max_digits=8,     # Debe coincidir con el modelo
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la cantidad disponible'
        })
    )

    class Meta:
        model = Producto
        exclude = ['fecha_agregado', 'agregado_por']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'num_cat': forms.TextInput(attrs={'class': 'form-control'}),
            'num_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'vencimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),   #Este vencimiento me convierte el widget en formato para captura del dato
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar solo estados válidos para edición
        estados_visibles = ['disponible','no_disponible']
        self.fields['estado'].queryset = EstadoRecurso.objects.filter(estado__in=estados_visibles)

        self.set_optional_fields()
        self.apply_bootstrap_classes()
        self.setup_category_filtering()
        self.order_choices_for_ux()
        self.fields['vencimiento'].input_formats = ['%Y-%m-%d']   #Al cargar el formulario de edición, la fecha se mostrará correctamente en el campo.

        self.fields['categoria'].widget.attrs.update({'id': 'id_categoria'})
        self.fields['subcategoria'].widget.attrs.update({'id': 'id_subcategoria'})

    def set_optional_fields(self):
        # Estos campos realmente pueden ser opcionales, los demás como nombre, categoria, sub, estado no.
        optional_fields = [
            'lote', 'marca', 'modelo', 'color', 'presentacion',
            'capacidad', 'accesorios', 'medida',
            'codigo', 'num_cat', 'num_serie', 'vencimiento',
            'descripcion', 'observacion'
    ]

        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False

    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

    def setup_category_filtering(self):
        self.fields['subcategoria'].queryset = Subcategoria.objects.none()

    def order_choices_for_ux(self):
        if hasattr(self.fields['categoria'], 'queryset'):
            self.fields['categoria'].queryset = self.fields['categoria'].queryset.order_by('nombre')
        if hasattr(self.fields['unidad_medida'], 'queryset'):
            self.fields['unidad_medida'].queryset = self.fields['unidad_medida'].queryset.order_by('nombre')
    
    def clean(self):
        cleaned_data = super().clean()
        codigo = cleaned_data.get('codigo')
        num_cat = cleaned_data.get('num_cat')
        num_serie = cleaned_data.get('num_serie')

        qs = Producto.objects.all()
        if self.instance.pk:
         qs = qs.exclude(pk=self.instance.pk)

        if codigo and qs.filter(codigo=codigo).exists():
         self.add_error('codigo', 'Este código ya está en uso.')

        if num_cat and qs.filter(num_cat=num_cat).exists():
            self.add_error('num_cat', 'Este número de catálogo ya existe.')

        if num_serie and qs.filter(num_serie=num_serie).exists():
            self.add_error('num_serie', 'Este número de serie ya está registrado.')

        # Lógica corregida para establecer el estado según la cantidad
        cantidad_disponible = cleaned_data.get('cantidad_disponible')
        estado = None  # Asegurarse de que esté definida

        if cantidad_disponible is not None:
         if cantidad_disponible > 0:
            estado = EstadoRecurso.objects.filter(estado='disponible').first()
        elif cantidad_disponible == 0:
            estado = EstadoRecurso.objects.filter(estado='no_disponible').first()

        if estado:
            cleaned_data['estado'] = estado

    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data.get('cantidad_disponible')
        if cantidad is None:
            raise forms.ValidationError("Este campo es obligatorio.")
        if cantidad < 0:
            raise forms.ValidationError("La cantidad no puede ser negativa.")
        return cantidad
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.cantidad_disponible == 0:
            instance.estado = EstadoRecurso.objects.get(estado='no_disponible')
        elif instance.cantidad_disponible > 0:
            instance.estado = EstadoRecurso.objects.get(estado='disponible')
        if commit:
            instance.save()
        return instance
