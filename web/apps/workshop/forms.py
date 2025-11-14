from django import forms


class VehicleSearchForm(forms.Form):
    """Formulario para buscar un vehículo por patente."""
    license_plate = forms.CharField(
        max_length=20,
        label="Patente",
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ABCD12'
        })
    )
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
    fire_station_id = forms.IntegerField(
        label="Cuartel",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_type_id = forms.IntegerField(
        label="Tipo de Vehículo",
        widget=forms.Select(attrs={'class': 'form-select'})
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
        label="VIN / Chasis",
        required=False,
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


class MaintenanceOrderForm(forms.Form):
    """Formulario para crear/editar una orden de mantención."""
    vehicle_id = forms.IntegerField(
        label="Vehículo",
        widget=forms.HiddenInput()
    )
    mileage = forms.IntegerField(
        label="Kilometraje de Ingreso",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 50000',
            'min': 0
        })
    )
    maintenance_type_id = forms.IntegerField(
        label="Tipo de Mantención",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    order_status_id = forms.IntegerField(
        label="Estado de la Orden",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    assigned_mechanic_id = forms.CharField(
        label="Mecánico Asignado",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    entry_date = forms.DateField(
        label="Fecha de Ingreso",
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


class MaintenanceTaskForm(forms.Form):
    """Formulario para crear/editar una tarea de mantención."""
    task_type_id = forms.IntegerField(
        label="Tipo de Tarea",
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
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    workshop_inventory_id = forms.IntegerField(
        label="Repuesto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity_used = forms.IntegerField(
        label="Cantidad",
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
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        label="Cantidad",
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Estante A-3'
        })
    )
    workshop_sku = forms.CharField(
        max_length=100,
        label="SKU Interno del Taller",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código interno (opcional)'
        })
    )


class InventoryUpdateForm(forms.Form):
    """Formulario para actualizar stock, costo y otros datos de un repuesto."""
    quantity = forms.IntegerField(
        label="Cantidad",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    current_cost = forms.DecimalField(
        label="Costo Actual (CLP)",
        max_digits=10,
        decimal_places=2,
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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    workshop_sku = forms.CharField(
        max_length=100,
        label="SKU Interno del Taller",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class SupplierForm(forms.Form):
    """Formulario para crear/editar un proveedor local del taller."""
    name = forms.CharField(
        max_length=255,
        label="Nombre del Proveedor",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Distribuidora Local'
        })
    )
    rut = forms.CharField(
        max_length=20,
        label="RUT",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678-9'
        })
    )
    address = forms.CharField(
        max_length=255,
        label="Dirección",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección del proveedor'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: +56912345678'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: contacto@proveedor.cl'
        })
    )


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



