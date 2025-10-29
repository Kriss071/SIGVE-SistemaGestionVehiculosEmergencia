from django import forms

class LoginForm(forms.Form):
    """
    Formulario para la autenticación de usuarios.

    Define los campos necesarios para el inicio de sesión (email y contraseña)
    y configura sus widgets y mensajes de error para ser renderizados en las plantillas.
    """
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
