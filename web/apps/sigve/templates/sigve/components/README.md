# Componentes Reutilizables SIGVE

Este directorio contiene componentes HTML reutilizables para el panel de administración SIGVE.

## Toast Container

### Ubicación
`toast_container.html`

### Descripción
Sistema unificado de notificaciones tipo "toast" para toda la aplicación SIGVE. Los toasts se muestran en la esquina superior derecha de la pantalla y se autocierran después de 5 segundos.

### Uso

#### 1. Incluir en el template base
```django
{% include 'sigve/components/toast_container.html' %}
```

#### 2. Usar desde JavaScript
```javascript
// Éxito
SIGVENotifications.success('Taller creado correctamente');

// Error
SIGVENotifications.error('No se pudo guardar el taller');

// Advertencia
SIGVENotifications.warning('El email ya está registrado');

// Información
SIGVENotifications.info('Recuerda completar todos los campos');

// Errores de validación (desde respuesta AJAX)
SIGVENotifications.showValidationErrors(data.errors);

// Personalizado
SIGVENotifications.show('Mensaje personalizado', 'info', 7000);
```

#### 3. Mensajes desde Django (automático)
Los mensajes del framework de Django se convierten automáticamente en toasts:

```python
from django.contrib import messages

messages.success(request, 'Operación exitosa')
messages.error(request, 'Ocurrió un error')
messages.warning(request, 'Advertencia importante')
messages.info(request, 'Información relevante')
```

### Tipos de Toast
- `success` - Verde, para operaciones exitosas
- `error` - Rojo, para errores
- `warning` - Amarillo, para advertencias
- `info` - Azul, para información general

### Características
- ✅ Se autocierran después de 5 segundos (configurable)
- ✅ Se pueden cerrar manualmente con el botón X
- ✅ No se acumulan de forma molesta
- ✅ Incluyen iconos para mejor visualización
- ✅ Prevención de XSS automática
- ✅ Compatible con modales
- ✅ Responsive

### Ventajas sobre alertas tradicionales
1. **No bloquean la interfaz**: El usuario puede seguir trabajando mientras se muestra la notificación
2. **Posicionamiento consistente**: Siempre en la esquina superior derecha
3. **Auto-desaparecen**: No requieren acción del usuario
4. **Funcionan con modales**: Las notificaciones se ven incluso cuando hay modales abiertos
5. **Sistema unificado**: Un solo método de notificación en toda la aplicación

### API Completa

```javascript
window.SIGVENotifications = {
    // Muestra una notificación personalizada
    show(message, type = 'info', duration = 5000),
    
    // Atajos para tipos específicos
    success(message),
    error(message),
    warning(message),
    info(message),
    
    // Para errores de validación de formularios
    showValidationErrors(errors)
}
```

### Ejemplo con AJAX
```javascript
fetch('/api/crear-taller/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        SIGVENotifications.success(data.message);
    } else if (data.errors) {
        SIGVENotifications.showValidationErrors(data.errors);
    }
})
.catch(error => {
    SIGVENotifications.error('Error de conexión');
});
```

