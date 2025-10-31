from django import forms
from typing import List, Dict


class EmployeeForm(forms.Form):
    """
    Formulario dinámico para Empleados.
    - Por defecto, está configurado para CREAR un nuevo empleado y su usuario en Auth.
    - Si se inicializa con un 'prefix', se adapta para ACTUALIZAR un empleado existente.
    """

    # Campos creación de usuario en Auth de Supabase
    email = forms.EmailField(
        label="Email del Nuevo Usuario",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Contraseña Temporal",
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="El usuario deberá cambiarla en su primer inicio de sesión."
    )

    # Campos creación de Employee
    first_name = forms.CharField(
        label="Nombres",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 12.345.678-9"})
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    role_id = forms.ChoiceField(
        label="Rol",
        choices=[],
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    workshop_id = forms.ChoiceField(
        label="Taller Asignado",
        choices=[('', '---------')], # Permitir que sea opcional
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    is_active = forms.BooleanField(
        label="¿Está Activo?",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    def __init__(self, *args, **kwargs):
        # El prefijo es útil para el formulario de actualización
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        # Si el formulario es para ACTUALIZAR (identificado por el prefijo)...
        if self.prefix:
            # 1. Eliminamos los campos que no se usan en la actualización.
            #    No se puede cambiar el email ni la contraseña desde aquí.
            del self.fields['email']
            del self.fields['password']

            # 2. AÑADIMOS el campo 'id' que SÍ es necesario para la actualización.
            #    Lo hacemos oculto porque se llenará con JS y el usuario no debe editarlo.
            self.fields['id'] = forms.UUIDField(widget=forms.HiddenInput())

    # --- Métodos para poblar los <select> ---

    def set_roles(self, roles: List[Dict]):
        """Actualiza las opciones de roles."""
        choices = [('', 'Seleccione un rol')]
        choices.extend([(str(r['id']), r['name']) for r in roles])
        self.fields['role_id'].choices = choices
    
    def set_workshops(self, workshops: List[Dict]):
        """Actualiza las opciones de talleres."""
        choices = [('', 'Ninguno / No aplica')]
        choices.extend([(str(w['id']), w['name']) for w in workshops])
        self.fields['workshop_id'].choices = choices

class WorkshopForm(forms.Form):
    """
    Formulario para la creación y edición de Talleres (Workshop).
    - Si se usa con un prefijo 'update', se añade un campo 'id' oculto.
    """
    
    # Campo 'id' para el formulario de actualización
    # Se añade en __init__ si hay prefijo
    
    name = forms.CharField(
        label="Nombre del Taller",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Taller Central Santiago"})
    )
    address = forms.CharField(
        label="Dirección",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. Principal 123, Santiago"})
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: +56912345678"})
    )
    email = forms.EmailField(
        label="Email de Contacto",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ej: contacto@taller.cl"})
    )
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        
        # Si el formulario es para ACTUALIZAR (identificado por el prefijo 'update')...
        if self.prefix:
            # Añadimos el campo 'id' (entero) que es necesario para la actualización.
            self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())

class SupplierForm(forms.Form):
    """
    Formulario para la creación y edición de Proveedores (Supplier).
    - Si se usa con un prefijo 'update', se añade un campo 'id' oculto.
    """
    
    name = forms.CharField(
        label="Nombre del Proveedor",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Repuestos Express S.A."})
    )
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 76.123.456-7"})
    )
    address = forms.CharField(
        label="Dirección",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. 10 de Julio 543, Santiago"})
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: +56221234567"})
    )
    email = forms.EmailField(
        label="Email de Contacto",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ej: ventas@repuestos.cl"})
    )
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        
        # Si el formulario es para ACTUALIZAR (identificado por el prefijo 'update')...
        if self.prefix:
            # Añadimos el campo 'id' (entero) que es necesario para la actualización.
            self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())


class VehicleTypeForm(forms.Form):
    """
    Formulario para la creación y edición de Tipos de Vehículo (VehicleType).
    """
    
    name = forms.CharField(
        label="Nombre del Tipo",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Carro Bomba"})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe brevemente este tipo de vehículo..."})
    )
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        
        if self.prefix:
            # Añadimos el campo 'id' (entero) para la actualización.
            self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())


class FireStationForm(forms.Form):
    """
    Formulario para la creación y edición de Cuarteles de Bomberos (FireStation).
    - Si se usa con un prefijo 'update', se añade un campo 'id' oculto.
    """
    
    name = forms.CharField(
        label="Nombre del Cuartel",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 1ª Cía. Bomberos de Santiago"})
    )
    address = forms.CharField(
        label="Dirección",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. Libertador Bernardo O'Higgins 113"})
    )
    commune_id = forms.ChoiceField(
        label="Comuna",
        choices=[('', '---------')],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        
        if self.prefix:
            self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())

    def set_communes(self, communes: List[Dict]):
        """Actualiza las opciones de comunas."""
        choices = [('', 'Seleccione una comuna')]
        choices.extend([(str(c['id']), c['name']) for c in communes])
        self.fields['commune_id'].choices = choices

class VehicleStatusForm(forms.Form):
    """
    Formulario para la creación y edición de VehicleStatus.
    """
    name = forms.CharField(
        label="Nombre",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Operativo"})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)

        if self.prefix:
            self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())