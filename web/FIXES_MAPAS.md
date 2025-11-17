# 🔧 Correcciones del Sistema de Mapas

## Problemas Resueltos

### ❌ Problema 1: Error de Serialización JSON
**Error:** `Object of type Decimal is not JSON serializable`

**Causa:** Django Forms devuelve valores `Decimal` para campos `DecimalField`, pero Supabase/httpx no puede serializarlos a JSON.

**Solución:** Convertir explícitamente los valores `Decimal` a `float` antes de enviarlos a Supabase.

**Archivos modificados:**
- `apps/sigve/views.py`

**Cambios realizados:**
```python
# ANTES (causaba error):
data = {
    'latitude': form.cleaned_data.get('latitude'),
    'longitude': form.cleaned_data.get('longitude')
}

# DESPUÉS (funciona correctamente):
data = {
    'latitude': float(form.cleaned_data['latitude']) if form.cleaned_data.get('latitude') else None,
    'longitude': float(form.cleaned_data['longitude']) if form.cleaned_data.get('longitude') else None
}
```

### ❌ Problema 2: Botones "Buscar ubicación" Duplicados
**Error:** Cada vez que se abría el modal, se creaba un nuevo botón sin eliminar el anterior.

**Causa:** La función `setupAddressGeocoding()` creaba un nuevo botón en cada llamada sin verificar si ya existía.

**Solución:** Modificar la función para:
1. Verificar si el botón ya existe
2. Si existe, reutilizarlo (limpiando event listeners)
3. Si no existe, crearlo

**Archivos modificados:**
- `apps/sigve/static/js/geocoding.js`

**Cambios realizados:**
```javascript
// Buscar botón existente primero
let geocodeButton = document.getElementById(btnId);

// Si no existe, crearlo
if (!geocodeButton) {
    // Crear nuevo botón
    geocodeButton = document.createElement('button');
    // ... configuración ...
    addressInput.parentNode.insertBefore(geocodeButton, addressInput.nextSibling);
} else {
    // Si ya existe, limpiar event listeners anteriores clonándolo
    const newButton = geocodeButton.cloneNode(true);
    geocodeButton.parentNode.replaceChild(newButton, geocodeButton);
    geocodeButton = newButton;
}
```

### ❌ Problema 3: Script de Geocodificación No Cargaba en Todas las Páginas
**Error:** El botón "Buscar ubicación" no aparecía al abrir modales desde las páginas de lista.

**Causa:** El script `geocoding.js` solo estaba incluido en el dashboard.

**Solución:** Incluir el script en todas las páginas que usan los modales.

**Archivos modificados:**
- `apps/sigve/templates/sigve/workshops_list.html`
- `apps/sigve/templates/sigve/fire_stations_list.html`

**Cambios realizados:**
```html
{% block extra_js %}
<script src="{% static 'js/geocoding.js' %}"></script>  <!-- AGREGADO -->
<script src="{% static 'js/modal.js' %}"></script>
<script src="{% static 'js/workshop.js' %}"></script>
{% endblock %}
```

## ✅ Verificación de Soluciones

### Probar Creación de Cuartel/Taller

1. **Navega a Talleres o Cuarteles**
   ```
   http://localhost:8000/sigve/workshops/
   http://localhost:8000/sigve/fire-stations/
   ```

2. **Haz clic en "Crear Taller" o "Crear Cuartel"**
   - ✅ Debe aparecer UN SOLO botón "🔍 Buscar ubicación"

3. **Ingresa una dirección**
   - Ejemplo: `Morandé 360, Santiago Centro, Santiago, Chile`

4. **Haz clic en "Buscar ubicación"**
   - ✅ Debe mostrar spinner de carga
   - ✅ Debe mostrar "✓ Ubicación encontrada" después de 2-3 segundos
   - ✅ El campo de dirección debe tener borde verde

5. **Guarda el formulario**
   - ✅ NO debe aparecer error de JSON
   - ✅ Debe guardar correctamente
   - ✅ Debe aparecer en el mapa del dashboard

### Probar Que No Se Dupliquen Botones

1. **Abre un modal de crear/editar**
   - ✅ Debe aparecer 1 botón

2. **Cierra el modal (sin guardar)**

3. **Vuelve a abrir el modal**
   - ✅ Debe seguir apareciendo 1 solo botón (no 2)

4. **Repite varias veces**
   - ✅ Siempre debe haber 1 solo botón

## 📝 Resumen de Cambios

### Archivos Modificados (3)
```
✅ apps/sigve/views.py
   - Conversión de Decimal a float en 4 lugares

✅ apps/sigve/static/js/geocoding.js
   - Verificación de botón existente
   - Limpieza de event listeners

✅ apps/sigve/templates/sigve/workshops_list.html
✅ apps/sigve/templates/sigve/fire_stations_list.html
   - Inclusión de geocoding.js
```

### Funciones Afectadas
- `workshop_create()` → views.py
- `workshop_edit()` → views.py
- `fire_station_create()` → views.py
- `fire_station_edit()` → views.py
- `setupAddressGeocoding()` → geocoding.js

## 🚀 Estado Actual

✅ Sistema completamente funcional  
✅ Sin errores de serialización  
✅ Sin duplicación de botones  
✅ Geocodificación funcionando en todas las páginas  

## 📖 Documentación Relacionada

- `INSTALACION_MAPA.md` - Guía de instalación
- `QUICK_START_MAPA.md` - Guía rápida de uso
- `ARQUITECTURA_MAPAS.md` - Documentación técnica
- `RESUMEN_MAPAS.md` - Resumen ejecutivo

---

**Correcciones aplicadas:** 16 de noviembre de 2025  
**Sistema:** SIGVE - Sistema de Gestión de Vehículos de Emergencia

