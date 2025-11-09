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


class UserCreateForm(forms.Form):
    """Formulario para crear usuarios completos (auth + perfil)."""
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@ejemplo.cl'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'})
    )
    role_id = forms.TypedChoiceField(
        label="Rol",
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    workshop_id = forms.TypedChoiceField(
        label="Taller",
        required=False,
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fire_station_id = forms.TypedChoiceField(
        label="Cuartel",
        required=False,
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        label="Activo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(
        self,
        *args,
        role_choices=None,
        workshop_choices=None,
        fire_station_choices=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.fields['role_id'].choices = role_choices or []
        self.fields['workshop_id'].choices = workshop_choices or []
        self.fields['fire_station_id'].choices = fire_station_choices or []

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')

        workshop_id = cleaned_data.get('workshop_id')
        fire_station_id = cleaned_data.get('fire_station_id')

        if workshop_id and fire_station_id:
            self.add_error(
                'fire_station_id',
                'Un usuario no puede estar asociado a un taller y un cuartel simultáneamente.'
            )

        return cleaned_data


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


