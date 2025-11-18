from django import forms


class VehicleSearchForm(forms.Form):
    """Formulario para buscar un vehículo por patente."""
    license_plate = forms.CharField(
        max_length=20,
        label="Patente",
        error_messages={
            'required': 'Por favor, ingresa una patente para buscar.',
            'max_length': 'La patente no puede exceder 20 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ABCD12',
            'autocomplete': 'off'
        })
    )


class VehicleCreateForm(forms.Form):
    """Formulario para crear un nuevo vehículo desde el taller."""
    license_plate = forms.CharField(
        max_length=20,
        label="Patente",
        error_messages={
            'required': 'Por favor, ingresa una patente.',
            'max_length': 'La patente no puede exceder 20 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ABCD12'
        })
    )
    brand = forms.CharField(
        max_length=100,
        label="Marca",
        error_messages={
            'required': 'Por favor, ingresa la marca del vehículo.',
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
            'required': 'Por favor, ingresa el modelo del vehículo.',
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
            'required': 'Por favor, ingresa el año del vehículo.',
            'invalid': 'Por favor, ingresa un año válido (entre 1900 y 2100).',
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
    fire_station_id = forms.IntegerField(
        label="Cuartel",
        error_messages={
            'required': 'Por favor, selecciona un cuartel.',
            'invalid': 'Por favor, selecciona un cuartel válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        error_messages={
            'required': 'Por favor, selecciona un tipo de vehículo.',
            'invalid': 'Por favor, selecciona un tipo de vehículo válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
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
        label="VIN / Chasis",
        error_messages={
            'required': 'Por favor, ingresa el número de chasis (VIN).',
            'max_length': 'El número de chasis (VIN) no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de chasis'
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
    
    def clean_license_plate(self):
        """Valida y normaliza la patente."""
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


class MaintenanceOrderForm(forms.Form):
    """Formulario para crear/editar una orden de mantención."""
    vehicle_id = forms.IntegerField(
        label="Vehículo",
        error_messages={
            'required': 'Debe seleccionarse un vehículo.',
            'invalid': 'El vehículo seleccionado no es válido.'
        },
        widget=forms.HiddenInput()
    )
    mileage = forms.IntegerField(
        label="Kilometraje de Ingreso",
        error_messages={
            'required': 'Por favor, ingresa el kilometraje de ingreso.',
            'invalid': 'Por favor, ingresa un kilometraje válido (número entero mayor o igual a 0).',
            'min_value': 'El kilometraje no puede ser negativo.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 50000',
            'min': 0
        })
    )
    maintenance_type_id = forms.IntegerField(
        label="Tipo de Mantención",
        error_messages={
            'required': 'Por favor, selecciona un tipo de mantención.',
            'invalid': 'Por favor, selecciona un tipo de mantención válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    order_status_id = forms.IntegerField(
        label="Estado de la Orden",
        error_messages={
            'required': 'Por favor, selecciona un estado para la orden.',
            'invalid': 'Por favor, selecciona un estado válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    assigned_mechanic_id = forms.CharField(
        label="Mecánico Asignado",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    entry_date = forms.DateField(
        label="Fecha de Ingreso",
        error_messages={
            'required': 'Por favor, selecciona una fecha de ingreso.',
            'invalid': 'Por favor, ingresa una fecha válida.'
        },
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    exit_date = forms.DateField(
        label="Fecha de Salida",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    observations = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Notas generales sobre la orden...'
        })
    )
    
    def clean_mileage(self):
        """Valida que el kilometraje sea válido."""
        mileage = self.cleaned_data.get('mileage')
        if mileage is not None and mileage < 0:
            raise forms.ValidationError('El kilometraje no puede ser negativo.')
        return mileage
    
    def clean_entry_date(self):
        """Valida que la fecha de ingreso sea válida."""
        entry_date = self.cleaned_data.get('entry_date')
        if entry_date:
            from datetime import date
            if entry_date > date.today():
                raise forms.ValidationError('La fecha de ingreso no puede ser futura.')
        return entry_date
    
    def clean_order_status_id(self):
        """Valida que el estado de orden no sea de finalización al crear."""
        order_status_id = self.cleaned_data.get('order_status_id')
        if order_status_id:
            # Importar aquí para evitar importaciones circulares
            from apps.workshop.services.vehicle_service import VehicleService
            from apps.workshop.services.order_service import OrderService
            
            # Obtener todos los estados
            all_statuses = VehicleService.get_order_statuses()
            selected_status = next(
                (s for s in all_statuses if s.get('id') == order_status_id),
                None
            )
            
            if selected_status:
                status_name = selected_status.get('name', '')
                # Verificar si es un estado de finalización
                if OrderService.is_completion_status(status_name):
                    raise forms.ValidationError(
                        f'No se puede crear una orden con el estado "{status_name}". '
                        'Solo se permiten estados activos al crear una orden.'
                    )
        
        return order_status_id


class MaintenanceTaskForm(forms.Form):
    """Formulario para crear/editar una tarea de mantención."""
    task_type_id = forms.IntegerField(
        label="Tipo de Tarea",
        error_messages={
            'required': 'Por favor, selecciona un tipo de tarea.',
            'invalid': 'Por favor, selecciona un tipo de tarea válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Detalle adicional de la tarea...'
        })
    )
    cost = forms.DecimalField(
        label="Costo de Mano de Obra (CLP)",
        max_digits=10,
        decimal_places=2,
        initial=0,
        error_messages={
            'required': 'Por favor, ingresa un costo de mano de obra.',
            'invalid': 'Por favor, ingresa un costo válido (mínimo 0).',
            'max_digits': 'El costo no puede exceder 10 dígitos.',
            'max_decimal_places': 'El costo no puede tener más de 2 decimales.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': 0,
            'step': '0.01'
        })
    )


class TaskPartForm(forms.Form):
    """Formulario para agregar un repuesto a una tarea."""
    maintenance_task_id = forms.IntegerField(
        label="Tarea",
        error_messages={
            'required': 'Por favor, selecciona una tarea.',
            'invalid': 'Por favor, selecciona una tarea válida.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    workshop_inventory_id = forms.IntegerField(
        label="Repuesto",
        error_messages={
            'required': 'Por favor, selecciona un repuesto del inventario.',
            'invalid': 'Por favor, selecciona un repuesto válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity_used = forms.IntegerField(
        label="Cantidad",
        error_messages={
            'required': 'Por favor, ingresa una cantidad.',
            'invalid': 'Por favor, ingresa una cantidad válida (mínimo 1).',
            'min_value': 'La cantidad debe ser mayor o igual a 1.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'min': 1
        })
    )


class InventoryAddForm(forms.Form):
    """Formulario para agregar un repuesto al inventario del taller."""
    spare_part_id = forms.IntegerField(
        label="Repuesto del Catálogo",
        error_messages={
            'required': 'Por favor, selecciona un repuesto del catálogo.',
            'invalid': 'Por favor, selecciona un repuesto válido.'
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        label="Cantidad",
        error_messages={
            'required': 'Por favor, ingresa una cantidad.',
            'invalid': 'Por favor, ingresa una cantidad válida (mínimo 1).',
            'min_value': 'La cantidad debe ser mayor o igual a 1.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'min': 1
        })
    )
    current_cost = forms.DecimalField(
        label="Costo de Compra (CLP)",
        max_digits=10,
        decimal_places=2,
        error_messages={
            'required': 'Por favor, ingresa un costo de compra.',
            'invalid': 'Por favor, ingresa un costo válido (mínimo 0).',
            'max_digits': 'El costo no puede exceder 10 dígitos.',
            'max_decimal_places': 'El costo no puede tener más de 2 decimales.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': 0,
            'step': '0.01'
        })
    )
    supplier_id = forms.IntegerField(
        label="Proveedor",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        max_length=100,
        label="Ubicación en Bodega",
        required=False,
        error_messages={
            'max_length': 'La ubicación no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Estante A-3'
        })
    )
    workshop_sku = forms.CharField(
        max_length=100,
        label="SKU Interno del Taller",
        required=False,
        error_messages={
            'max_length': 'El SKU interno no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código interno (opcional)'
        })
    )
    
    def clean_quantity(self):
        """Valida que la cantidad sea positiva."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a cero.')
        return quantity
    
    def clean_current_cost(self):
        """Valida que el costo sea positivo."""
        current_cost = self.cleaned_data.get('current_cost')
        if current_cost is not None and current_cost < 0:
            raise forms.ValidationError('El costo debe ser mayor o igual a cero.')
        return current_cost
    
    def clean_workshop_sku(self):
        """Normaliza el SKU interno."""
        workshop_sku = self.cleaned_data.get('workshop_sku')
        if workshop_sku:
            return workshop_sku.strip()
        return workshop_sku


class InventoryUpdateForm(forms.Form):
    """Formulario para actualizar stock, costo y otros datos de un repuesto."""
    quantity = forms.IntegerField(
        label="Cantidad",
        error_messages={
            'required': 'Por favor, ingresa una cantidad.',
            'invalid': 'Por favor, ingresa una cantidad válida (mínimo 0).',
            'min_value': 'La cantidad no puede ser negativa.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    current_cost = forms.DecimalField(
        label="Costo Actual (CLP)",
        max_digits=10,
        decimal_places=2,
        error_messages={
            'required': 'Por favor, ingresa un costo actual.',
            'invalid': 'Por favor, ingresa un costo válido (mínimo 0).',
            'max_digits': 'El costo no puede exceder 10 dígitos.',
            'max_decimal_places': 'El costo no puede tener más de 2 decimales.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'step': '0.01'
        })
    )
    supplier_id = forms.IntegerField(
        label="Proveedor",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        max_length=100,
        label="Ubicación",
        required=False,
        error_messages={
            'max_length': 'La ubicación no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    workshop_sku = forms.CharField(
        max_length=100,
        label="SKU Interno del Taller",
        required=False,
        error_messages={
            'max_length': 'El SKU interno no puede exceder 100 caracteres.'
        },
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_quantity(self):
        """Valida que la cantidad no sea negativa."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return quantity
    
    def clean_current_cost(self):
        """Valida que el costo no sea negativa."""
        current_cost = self.cleaned_data.get('current_cost')
        if current_cost is not None and current_cost < 0:
            raise forms.ValidationError('El costo no puede ser negativo.')
        return current_cost
    
    def clean_workshop_sku(self):
        """Normaliza el SKU interno."""
        workshop_sku = self.cleaned_data.get('workshop_sku')
        if workshop_sku:
            return workshop_sku.strip()
        return workshop_sku


class SupplierForm(forms.Form):
    """Formulario para crear/editar un proveedor local del taller."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Proveedor",
        error_messages={
            'required': 'Por favor, ingresa un nombre para el proveedor.',
            'max_length': 'El nombre del proveedor no puede exceder 255 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Distribuidora Local'
        })
    )
    rut = forms.CharField(
        max_length=20,
        label="RUT",
        required=False,
        error_messages={
            'max_length': 'El RUT no puede exceder 20 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678-9'
        })
    )
    address = forms.CharField(
        max_length=255,
        label="Dirección",
        required=False,
        error_messages={
            'max_length': 'La dirección no puede exceder 255 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección del proveedor'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        error_messages={
            'max_length': 'El teléfono no puede exceder 20 caracteres.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: +56912345678'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        error_messages={
            'invalid': 'Por favor, ingresa un correo electrónico válido.',
            'max_length': 'El correo electrónico no puede exceder 254 caracteres.'
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: contacto@proveedor.cl'
        })
    )
    
    def clean(self):
        """Limpia y valida los datos del formulario."""
        cleaned_data = super().clean()
        
        # Convertir cadenas vacías a None para campos opcionales
        rut = cleaned_data.get('rut')
        if rut is not None and isinstance(rut, str) and rut.strip() == '':
            cleaned_data['rut'] = None
        
        address = cleaned_data.get('address')
        if address is not None and isinstance(address, str) and address.strip() == '':
            cleaned_data['address'] = None
        
        phone = cleaned_data.get('phone')
        if phone is not None and isinstance(phone, str) and phone.strip() == '':
            cleaned_data['phone'] = None
        
        email = cleaned_data.get('email')
        if email is not None and isinstance(email, str) and email.strip() == '':
            cleaned_data['email'] = None
        
        return cleaned_data


class EmployeeForm(forms.Form):
    """Formulario para editar información de un empleado."""
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


class EmployeeCreateForm(forms.Form):
    """Formulario para crear un nuevo empleado del taller."""
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'empleado@ejemplo.cl'
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
    role_id = forms.IntegerField(
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data


class DataRequestForm(forms.Form):
    """Formulario para crear una solicitud a SIGVE."""
    request_type_id = forms.IntegerField(
        label="Tipo de Solicitud",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Los campos dinámicos se agregan via JavaScript basándose en el form_schema



