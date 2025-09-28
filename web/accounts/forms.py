from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        error_messages={'invalid': 'Ingresa un correo electrónico válido.'},
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        }),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        }),
    )
