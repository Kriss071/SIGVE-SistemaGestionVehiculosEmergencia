from django import forms


class WorkshopForm(forms.Form):
    """Formulario para crear/editar talleres."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Taller",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mecánica Rápida'})
    )
    address = forms.CharField(
        max_length=255,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Principal 123'})
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'})
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: contacto@taller.cl'})
    )


class FireStationForm(forms.Form):
    """Formulario para crear/editar cuarteles."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Cuartel",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Primera Compañía'})
    )
    address = forms.CharField(
        max_length=255,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle Bomberos 456'})
    )
    commune_id = forms.IntegerField(
        label="Comuna",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class SparePartForm(forms.Form):
    """Formulario para crear/editar repuestos maestros."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Repuesto",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Filtro de Aceite'})
    )
    sku = forms.CharField(
        max_length=100,
        label="SKU (Código SIGVE)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: FO-001'})
    )
    brand = forms.CharField(
        max_length=255,
        label="Marca",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mann Filter'})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del repuesto'})
    )


class SupplierForm(forms.Form):
    """Formulario para crear/editar proveedores."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Proveedor",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Distribuidora ABC'})
    )
    rut = forms.CharField(
        max_length=20,
        label="RUT",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'})
    )
    address = forms.CharField(
        max_length=255,
        label="Dirección",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'})
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )


class CatalogItemForm(forms.Form):
    """Formulario genérico para items de catálogo."""
    name = forms.CharField(
        max_length=255,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del item'})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'})
    )


class UserProfileForm(forms.Form):
    """Formulario para editar perfil de usuario."""
    first_name = forms.CharField(
        max_length=255,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=255,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    rut = forms.CharField(
        max_length=20,
        label="RUT",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'})
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role_id = forms.IntegerField(
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        label="Activo",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class RejectRequestForm(forms.Form):
    """Formulario para rechazar una solicitud."""
    admin_notes = forms.CharField(
        label="Motivo del Rechazo",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explica por qué se rechaza esta solicitud...'
        })
    )


