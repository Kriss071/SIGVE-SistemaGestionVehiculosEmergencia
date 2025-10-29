from django import forms


class RoleForm(forms.Form):
    """
    Formulario para la creación y edición de Roles.
    """
    name = forms.CharField(
        label="Nombre del Rol",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Administrador"})
    )
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe los permisos y responsabilidades de este rol."})
    )