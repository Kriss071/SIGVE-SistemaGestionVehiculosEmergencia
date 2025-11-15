from django import forms


class VehicleForm(forms.Form):
    """Formulario para crear/editar vehículos."""
    
    # Campos no editables después de creación (solo en creación)
    license_plate = forms.CharField(
        max_length=20,
        label="Patente",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: AA-BB-12'
        })
    )
    engine_number = forms.CharField(
        max_length=100,
        label="Número de Motor",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de motor'
        })
    )
    vin = forms.CharField(
        max_length=100,
        label="Número de Chasis (VIN)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VIN'
        })
    )
    
    # Campos editables
    brand = forms.CharField(
        max_length=100,
        label="Marca",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mercedes-Benz'
        })
    )
    model = forms.CharField(
        max_length=100,
        label="Modelo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Atego 1725'
        })
    )
    year = forms.IntegerField(
        label="Año",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 2020',
            'min': 1900,
            'max': 2100
        })
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_status_id = forms.IntegerField(
        label="Estado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Campos opcionales editables
    mileage = forms.IntegerField(
        label="Kilometraje",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 50000',
            'min': 0
        })
    )
    oil_capacity_liters = forms.DecimalField(
        label="Capacidad de Aceite (litros)",
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12.5',
            'step': '0.01',
            'min': 0
        })
    )
    registration_date = forms.DateField(
        label="Fecha de Inscripción",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    next_revision_date = forms.DateField(
        label="Próxima Revisión Técnica",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    # Catálogos opcionales
    fuel_type_id = forms.IntegerField(
        label="Tipo de Combustible",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transmission_type_id = forms.IntegerField(
        label="Tipo de Transmisión",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    oil_type_id = forms.IntegerField(
        label="Tipo de Aceite",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    coolant_type_id = forms.IntegerField(
        label="Tipo de Refrigerante",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class VehicleCreateForm(VehicleForm):
    """Formulario específico para crear vehículos (incluye todos los campos)."""
    pass


class VehicleEditForm(forms.Form):
    """Formulario para editar vehículos (excluye campos no editables)."""
    
    # Solo campos editables
    brand = forms.CharField(
        max_length=100,
        label="Marca",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mercedes-Benz'
        })
    )
    model = forms.CharField(
        max_length=100,
        label="Modelo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Atego 1725'
        })
    )
    year = forms.IntegerField(
        label="Año",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 2020',
            'min': 1900,
            'max': 2100
        })
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_status_id = forms.IntegerField(
        label="Estado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mileage = forms.IntegerField(
        label="Kilometraje",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 50000',
            'min': 0
        })
    )
    oil_capacity_liters = forms.DecimalField(
        label="Capacidad de Aceite (litros)",
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12.5',
            'step': '0.01',
            'min': 0
        })
    )
    registration_date = forms.DateField(
        label="Fecha de Inscripción",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    next_revision_date = forms.DateField(
        label="Próxima Revisión Técnica",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fuel_type_id = forms.IntegerField(
        label="Tipo de Combustible",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transmission_type_id = forms.IntegerField(
        label="Tipo de Transmisión",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    oil_type_id = forms.IntegerField(
        label="Tipo de Aceite",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    coolant_type_id = forms.IntegerField(
        label="Tipo de Refrigerante",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class UserProfileForm(forms.Form):
    """Formulario para editar perfil de usuario del cuartel."""
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678'
        })
    )
    role_id = forms.TypedChoiceField(
        label="Rol",
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        label="Activo",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, role_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role_id'].choices = role_choices or []

