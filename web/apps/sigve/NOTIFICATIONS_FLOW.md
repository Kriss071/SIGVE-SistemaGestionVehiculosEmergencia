# Flujo de Notificaciones - Dashboard SIGVE

## 🐛 Problema Identificado

Las notificaciones se **duplicaban** porque:

1. Al enviar el formulario via AJAX, Django guardaba el mensaje en `messages.success()` o `messages.error()`
2. El JavaScript mostraba inmediatamente los errores como toasts
3. Al recargar la página con `window.location.reload()`, los mensajes guardados en la sesión de Django se convertían **de nuevo** en toasts
4. Resultado: **mensajes duplicados o acumulados**

## ✅ Solución Implementada

Ahora las vistas **solo guardan mensajes en Django messages cuando NO es una petición AJAX**:

### Flujo Anterior (❌ Incorrecto)

```python
# ❌ MAL: Guarda el mensaje antes de verificar si es AJAX
messages.success(request, 'Taller creado correctamente')

if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return JsonResponse({'success': True, 'message': '...'})
    
return redirect('sigve:workshops_list')
```

**Problema**: El mensaje se guarda en la sesión incluso cuando es AJAX, causando duplicados al recargar.

### Flujo Nuevo (✅ Correcto)

```python
# ✅ BIEN: Verifica primero si es AJAX
if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return JsonResponse({'success': True, 'message': '...'})

# Solo llega aquí si NO es AJAX
messages.success(request, 'Taller creado correctamente')
return redirect('sigve:workshops_list')
```

**Ventaja**: Los mensajes SOLO se guardan cuando la petición no es AJAX, evitando duplicados.

## 📊 Flujo Completo - Caso de Éxito

```
Usuario hace clic en "Guardar Taller"
        ↓
JavaScript envía POST via AJAX (con header X-Requested-With)
        ↓
Vista Django detecta que es AJAX
        ↓
Vista retorna JsonResponse con success y message (SIN guardar en messages)
        ↓
JavaScript muestra toast de éxito INMEDIATAMENTE
        ↓
JavaScript cierra el modal
        ↓
JavaScript espera 1.5 segundos (para que usuario vea el toast)
        ↓
JavaScript recarga la página (window.location.reload)
        ↓
NO hay mensajes pendientes en la sesión
        ↓
✅ Usuario vio el mensaje de éxito
✅ NO aparecen toasts duplicados al recargar
```

## 📊 Flujo Completo - Caso de Error

```
Usuario envía formulario con errores
        ↓
JavaScript envía POST via AJAX
        ↓
Vista detecta errores de validación
        ↓
Vista retorna JsonResponse con errors (SIN guardar en messages)
        ↓
JavaScript recibe la respuesta
        ↓
JavaScript muestra errores inmediatamente como toasts
        ↓
Usuario corrige errores y reenvía
        ↓
✅ Los toasts anteriores ya se auto-cerraron
✅ NO hay acumulación de mensajes
```

## 🔧 Archivos Modificados

### 1. `web/apps/sigve/views.py`

**Funciones actualizadas:**
- `workshop_create()` (líneas 135-146)
- `fire_station_create()` (líneas 251-262)
- `spare_part_create()` (líneas 369-380)

**Cambio clave:**
```python
# Antes
messages.success(request, '...')
if is_ajax:
    return JsonResponse(...)

# Ahora
if is_ajax:
    return JsonResponse(...)
messages.success(request, '...')  # Solo si NO es AJAX
```

### 2. `web/apps/sigve/templates/sigve/modals/*.html`

**Archivos actualizados:**
- `workshop_modal.html`
- `fire_station_modal.html`
- `spare_part_modal.html`

**Cambio clave:**
```javascript
// Mostrar toast de éxito ANTES de recargar
if (data.success) {
    SIGVENotifications.success(data.message);
    modalInstance.hide();
    setTimeout(() => {
        window.location.reload();
    }, 1500);  // Espera 1.5s para que usuario vea el toast
}
```

**Ventaja**: El usuario ve el mensaje inmediatamente, y como NO guardamos en Django messages, NO hay duplicados al recargar.

## 🎯 Ventajas del Nuevo Sistema

1. ✅ **Sin duplicados**: Los mensajes de éxito solo aparecen UNA vez (antes de recargar, no se guardan en session)
2. ✅ **Feedback inmediato**: Los mensajes aparecen al instante (éxito y errores)
3. ✅ **No se acumulan**: Los toasts se auto-cierran después de 5 segundos
4. ✅ **Experiencia fluida**: El usuario ve el resultado antes de que se recargue la página
5. ✅ **Consistente**: Un solo flujo para todas las notificaciones
6. ✅ **Predecible**: El comportamiento es el mismo para todas las vistas

## 🧪 Casos de Prueba

### Caso 1: Crear taller con éxito
1. Abrir modal "Crear Taller"
2. Completar formulario correctamente
3. Click en "Guardar"
4. **Resultado esperado**: 
   - Aparece **toast verde inmediatamente** con "Taller creado correctamente"
   - Modal se cierra
   - Después de 1.5 segundos, página se recarga
   - Al recargar, **NO aparece ningún mensaje duplicado**

### Caso 2: Error de validación
1. Abrir modal "Crear Taller"
2. Dejar campo "Nombre" vacío
3. Click en "Guardar"
4. **Resultado esperado**:
   - Modal permanece abierto
   - Aparece **toast rojo** con "name: Este campo es obligatorio"
   - Toast se auto-cierra después de 5 segundos
5. Completar el campo y reenviar
6. **Resultado esperado**:
   - **NO aparecen los errores anteriores**
   - Modal se cierra y recarga
   - Aparece toast de éxito

### Caso 3: Múltiples errores seguidos de éxito
1. Abrir modal "Crear Taller"
2. Dejar varios campos vacíos
3. Click en "Guardar"
4. **Resultado esperado**:
   - Aparecen **múltiples toasts rojos** (uno por cada error)
   - Todos se apilan en la esquina superior derecha
   - Todos se auto-cierran después de 5 segundos
5. Corregir los errores y guardar nuevamente
6. **Resultado esperado**:
   - Aparece **UN solo toast verde** de éxito
   - Los toasts de error anteriores ya se auto-cerraron
   - **NO hay acumulación de errores antiguos**
   - Modal se cierra y página se recarga después de 1.5s

## 🔍 Debugging

Si aún ves duplicados, verifica:

1. **Cache del navegador**: Limpia la caché y recarga con Ctrl+Shift+R
2. **Múltiples includes**: Asegúrate de que `toast_container.html` solo se incluye UNA vez en `base.html`
3. **Mensajes en sesión**: Verifica que no haya mensajes antiguos con:
   ```python
   # En la vista
   from django.contrib import messages
   messages.get_messages(request).used = True  # Limpiar mensajes antiguos
   ```

## 📝 Notas Técnicas

- **AJAX Detection**: Usamos el header `X-Requested-With: XMLHttpRequest`
- **Toast Duration**: 5000ms (5 segundos) configurado en `toast_container.html`
- **Z-Index**: Los toasts tienen `z-index: 9999` para aparecer sobre modales
- **Auto-cleanup**: Los toasts se eliminan del DOM después de cerrarse

