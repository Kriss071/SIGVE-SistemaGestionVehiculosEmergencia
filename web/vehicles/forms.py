from django import forms
from typing import List, Dict


class VehicleForm(forms.Form):
    # Campos principales obligatorios
    license_plate = forms.CharField(
        label="Patente",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "required": True})
    )
    brand = forms.CharField(
        label="Marca",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "required": True})
    )
    model = forms.CharField(
        label="Modelo",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "required": True})
    )
    year = forms.IntegerField(
        label="Año",
        min_value=1900,
        widget=forms.NumberInput(attrs={"class": "form-control", "required": True})
    )
    
    # Campos obligatorios con Foreign Keys
    fire_station_id = forms.ChoiceField(
        label="Cuartel de Bomberos",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control", "required": True})
    )
    vehicle_type_id = forms.ChoiceField(
        label="Tipo de Vehículo",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control", "required": True})
    )
    vehicle_status_id = forms.ChoiceField(
        label="Estado del Vehículo",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control", "required": True})
    )
    
    # Campos opcionales
    engine_number = forms.CharField(
        label="Número de Motor",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    vin = forms.CharField(
        label="VIN (Número de Chasis)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    mileage = forms.IntegerField(
        label="Kilometraje",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    mileage_last_updated = forms.DateField(
        label="Fecha Último Kilometraje",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    oil_capacity_liters = forms.DecimalField(
        label="Capacidad de Aceite (L)",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"})
    )
    registration_date = forms.DateField(
        label="Fecha de Inscripción",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    next_revision_date = forms.DateField(
        label="Próxima Revisión Técnica",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    
    # Campos opcionales con Foreign Keys
    fuel_type_id = forms.ChoiceField(
        label="Tipo de Combustible",
        choices=[('', '---------')],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    transmission_type_id = forms.ChoiceField(
        label="Tipo de Transmisión",
        choices=[('', '---------')],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    oil_type_id = forms.ChoiceField(
        label="Tipo de Aceite",
        choices=[('', '---------')],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    coolant_type_id = forms.ChoiceField(
        label="Tipo de Refrigerante",
        choices=[('', '---------')],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Los choices se actualizarán desde la vista antes de usar el formulario
    
    def set_fire_stations(self, fire_stations: List[Dict]):
        """Actualiza las opciones de cuarteles de bomberos"""
        choices = [('', 'Seleccione un cuartel')]
        choices.extend([(str(s['id']), s['name']) for s in fire_stations])
        self.fields['fire_station_id'].choices = choices
    
    def set_vehicle_types(self, vehicle_types: List[Dict]):
        """Actualiza las opciones de tipos de vehículos"""
        choices = [('', 'Seleccione un tipo')]
        choices.extend([(str(t['id']), t['name']) for t in vehicle_types])
        self.fields['vehicle_type_id'].choices = choices
    
    def set_vehicle_statuses(self, vehicle_statuses: List[Dict]):
        """Actualiza las opciones de estados de vehículos"""
        choices = [('', 'Seleccione un estado')]
        choices.extend([(str(s['id']), s['name']) for s in vehicle_statuses])
        self.fields['vehicle_status_id'].choices = choices
    
    def set_fuel_types(self, fuel_types: List[Dict]):
        """Actualiza las opciones de tipos de combustible"""
        choices = [('', '---------')]
        choices.extend([(str(t['id']), t['name']) for t in fuel_types])
        self.fields['fuel_type_id'].choices = choices
    
    def set_transmission_types(self, transmission_types: List[Dict]):
        """Actualiza las opciones de tipos de transmisión"""
        choices = [('', '---------')]
        choices.extend([(str(t['id']), t['name']) for t in transmission_types])
        self.fields['transmission_type_id'].choices = choices
    
    def set_oil_types(self, oil_types: List[Dict]):
        """Actualiza las opciones de tipos de aceite"""
        choices = [('', '---------')]
        choices.extend([(str(t['id']), t['name']) for t in oil_types])
        self.fields['oil_type_id'].choices = choices
    
    def set_coolant_types(self, coolant_types: List[Dict]):
        """Actualiza las opciones de tipos de refrigerante"""
        choices = [('', '---------')]
        choices.extend([(str(t['id']), t['name']) for t in coolant_types])
        self.fields['coolant_type_id'].choices = choices

