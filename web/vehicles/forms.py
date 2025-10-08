from django import forms


class VehicleForm(forms.Form):
    patente = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    estado_mantencion = forms.ChoiceField(
        choices=[
            ("disponible", "Disponible"),
            ("en_mantenimiento", "En Mantenimiento"),
            ("fuera_de_servicio", "Fuera de Servicio"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    kilometraje_actual = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    tipo_vehiculo = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    marca = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    modelo = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    anio = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    fecha_ingreso = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    observaciones = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"class": "form-control"})
    )
