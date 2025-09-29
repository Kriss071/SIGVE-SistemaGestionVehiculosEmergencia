from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        error_messages={'invalid': 'Ingresa un correo electrónico válido.'},
        widget=forms.EmailInput(attrs={
            'class': 'login-form-input',
            'placeholder': 'Correo electrónico'
        }),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'login-form-input',
            'placeholder': 'Ingresa tu contraseña'
        }),
    )
