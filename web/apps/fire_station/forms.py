from django import forms


class VehicleForm(forms.Form):
    """Formulario para crear/editar vehículos."""
    
    # Campos no editables después de creación (solo en creación)
    license_plate = forms.CharField(
        max_length=20,
        label="Patente",
        error_messages={
            'required': 'Por favor, ingresa una patente.',
            'max_length': 'La patente no puede exceder 20 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: AA-BB-12'
        })
    )
    engine_number = forms.CharField(
        max_length=100,
        label="Número de Motor",
        error_messages={
            'required': 'Por favor, ingresa el número de motor.',
            'max_length': 'El número de motor no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de motor'
        })
    )
    vin = forms.CharField(
        max_length=100,
        label="Número de Chasis (VIN)",
        error_messages={
            'required': 'Por favor, ingresa el número de chasis (VIN).',
            'max_length': 'El número de chasis (VIN) no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VIN'
        })
    )
    
    # Campos editables
    brand = forms.CharField(
        max_length=100,
        label="Marca",
        error_messages={
            'required': 'Por favor, ingresa una marca.',
            'max_length': 'La marca no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mercedes-Benz'
        })
    )
    model = forms.CharField(
        max_length=100,
        label="Modelo",
        error_messages={
            'required': 'Por favor, ingresa un modelo.',
            'max_length': 'El modelo no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Atego 1725'
        })
    )
    year = forms.IntegerField(
        label="Año",
        min_value=1900,
        max_value=2100,
        error_messages={
            'required': 'Por favor, ingresa un año.',
            'invalid': 'Por favor, ingresa un año válido.',
            'min_value': 'El año debe ser mayor o igual a 1900.',
            'max_value': 'El año debe ser menor o igual a 2100.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 2020',
            'min': 1900,
            'max': 2100
        })
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        error_messages={
            'required': 'Por favor, selecciona un tipo de vehículo.',
            'invalid': 'El tipo de vehículo seleccionado no es válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_status_id = forms.IntegerField(
        label="Estado",
        error_messages={
            'required': 'Por favor, selecciona un estado.',
            'invalid': 'El estado seleccionado no es válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Campos opcionales editables
    mileage = forms.IntegerField(
        label="Kilometraje",
        required=False,
        error_messages={
            'invalid': 'Por favor, ingresa un kilometraje válido (número entero mayor o igual a 0).',
            'min_value': 'El kilometraje no puede ser negativo.'
        },
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
        error_messages={
            'invalid': 'Por favor, ingresa una capacidad de aceite válida.',
            'max_digits': 'La capacidad de aceite no puede exceder 5 dígitos.',
            'max_decimal_places': 'La capacidad de aceite no puede tener más de 2 decimales.'
        },
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

    def clean_license_plate(self):
        value = (self.cleaned_data.get('license_plate') or '').strip().upper()
        if not value:
            raise forms.ValidationError('Por favor, ingresa una patente.')
        # Permitir letras, números y guiones, largo razonable
        import re
        if not re.fullmatch(r'[A-Z0-9\-]{4,20}', value):
            raise forms.ValidationError('La patente debe contener 4 a 20 caracteres alfanuméricos o guiones.')
        return value
    
    def clean_engine_number(self):
        """Valida y normaliza el número de motor."""
        value = (self.cleaned_data.get('engine_number') or '').strip()
        if not value:
            raise forms.ValidationError('Por favor, ingresa el número de motor.')
        if len(value) > 100:
            raise forms.ValidationError('El número de motor no puede exceder 100 caracteres.')
        return value
    
    def clean_vin(self):
        """Valida y normaliza el VIN."""
        value = (self.cleaned_data.get('vin') or '').strip()
        if not value:
            raise forms.ValidationError('Por favor, ingresa el número de chasis (VIN).')
        if len(value) > 100:
            raise forms.ValidationError('El número de chasis (VIN) no puede exceder 100 caracteres.')
        return value


class VehicleCreateForm(VehicleForm):
    """Formulario específico para crear vehículos (incluye todos los campos)."""
    pass


class VehicleEditForm(forms.Form):
    """Formulario para editar vehículos (excluye campos no editables)."""
    
    # Solo campos editables
    brand = forms.CharField(
        max_length=100,
        label="Marca",
        error_messages={
            'required': 'Por favor, ingresa una marca.',
            'max_length': 'La marca no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mercedes-Benz'
        })
    )
    model = forms.CharField(
        max_length=100,
        label="Modelo",
        error_messages={
            'required': 'Por favor, ingresa un modelo.',
            'max_length': 'El modelo no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Atego 1725'
        })
    )
    year = forms.IntegerField(
        label="Año",
        error_messages={
            'required': 'Por favor, ingresa un año.',
            'invalid': 'Por favor, ingresa un año válido.',
            'min_value': 'El año debe ser mayor o igual a 1900.',
            'max_value': 'El año debe ser menor o igual a 2100.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 2020',
            'min': 1900,
            'max': 2100
        })
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        error_messages={
            'required': 'Por favor, selecciona un tipo de vehículo.',
            'invalid': 'El tipo de vehículo seleccionado no es válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_status_id = forms.IntegerField(
        label="Estado",
        error_messages={
            'required': 'Por favor, selecciona un estado.',
            'invalid': 'El estado seleccionado no es válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mileage = forms.IntegerField(
        label="Kilometraje",
        required=False,
        error_messages={
            'invalid': 'Por favor, ingresa un kilometraje válido (número entero mayor o igual a 0).',
            'min_value': 'El kilometraje no puede ser negativo.'
        },
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
        error_messages={
            'invalid': 'Por favor, ingresa una capacidad de aceite válida.',
            'max_digits': 'La capacidad de aceite no puede exceder 5 dígitos.',
            'max_decimal_places': 'La capacidad de aceite no puede tener más de 2 decimales.'
        },
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


class UserCreateForm(forms.Form):
    """Formulario para crear un nuevo usuario del cuartel."""
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@ejemplo.cl'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
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
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, role_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role_id'].choices = role_choices or []

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError({
                    'password_confirm': 'Las contraseñas no coinciden.'
                })
        
        return cleaned_data


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

