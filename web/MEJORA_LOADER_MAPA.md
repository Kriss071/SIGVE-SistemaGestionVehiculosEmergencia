# 🔄 Mejora: Loader para el Mapa

## ✨ Mejora Implementada

Se ha agregado un **loader visual** que se muestra mientras el mapa carga las ubicaciones, mejorando significativamente la experiencia del usuario.

## 🎯 Problema Anterior

Cuando se cargaba el dashboard, el mapa aparecía vacío durante 1-3 segundos mientras se obtenían las ubicaciones desde la API, lo que podía confundir al usuario haciéndole pensar que no había datos o que algo no funcionaba correctamente.

## ✅ Solución Implementada

### 1. Loader Visual con Spinner

Se agregó un overlay sobre el mapa que muestra:
- Spinner animado de Bootstrap
- Texto "Cargando ubicaciones..."
- Fondo semi-transparente para mejor visibilidad

### 2. Estados del Mapa

El sistema ahora maneja 3 estados posibles:

#### Estado 1: **Cargando** (Inicial)
```
┌─────────────────────────────────┐
│                                 │
│         ⟳  (spinner)            │
│   Cargando ubicaciones...       │
│                                 │
└─────────────────────────────────┘
```

#### Estado 2: **Con Datos** (Éxito)
```
┌─────────────────────────────────┐
│  🗺️  Mapa con marcadores       │
│  📍 Talleres (azul)             │
│  📍 Cuarteles (rojo)            │
└─────────────────────────────────┘
```

#### Estado 3: **Sin Ubicaciones** (Vacío)
```
┌─────────────────────────────────┐
│         📍 (icono grande)       │
│  No hay ubicaciones registradas │
│  Agrega coordenadas a tus...    │
└─────────────────────────────────┘
```

#### Estado 4: **Error** (Fallo de Carga)
```
┌─────────────────────────────────┐
│         ⚠️  (icono de alerta)   │
│    Error al cargar el mapa      │
│    [Botón Reintentar]           │
└─────────────────────────────────┘
```

## 📝 Archivos Modificados

### 1. `apps/sigve/templates/sigve/dashboard.html`

**Cambio:** Agregado HTML del loader

```html
<!-- ANTES -->
<div class="card-body p-0">
    <div id="map" style="height: 500px; width: 100%;"></div>
</div>

<!-- DESPUÉS -->
<div class="card-body p-0 position-relative">
    <div id="map" style="height: 500px; width: 100%;"></div>
    
    <!-- Loader del mapa -->
    <div id="mapLoader" class="position-absolute top-0 start-0 w-100 h-100 
         d-flex align-items-center justify-content-center 
         bg-white bg-opacity-75" style="z-index: 1000;">
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted mb-0">Cargando ubicaciones...</p>
        </div>
    </div>
</div>
```

### 2. `apps/sigve/static/js/dashboard.js`

**Cambios realizados:**

#### a) Ocultar loader cuando carga exitosamente
```javascript
// Ocultar loader después de cargar todo
if (mapLoader) {
    mapLoader.style.display = 'none';
}
```

#### b) Mostrar mensaje si no hay ubicaciones
```javascript
// Mostrar mensaje si no hay ubicaciones
const totalMarkers = workshopMarkers.length + fireStationMarkers.length;
if (totalMarkers === 0) {
    showNoLocationsMessage();
}
```

#### c) Nueva función: `showNoLocationsMessage()`
```javascript
function showNoLocationsMessage() {
    const mapLoader = document.getElementById('mapLoader');
    if (mapLoader) {
        mapLoader.innerHTML = `
            <div class="text-center">
                <i class="bi bi-geo-alt display-1 text-muted mb-3"></i>
                <h5 class="text-muted">No hay ubicaciones registradas</h5>
                <p class="text-muted mb-0">
                    Agrega coordenadas a tus talleres y cuarteles para verlos en el mapa
                </p>
            </div>
        `;
        mapLoader.style.display = 'flex';
    }
}
```

#### d) Nueva función: `showErrorMessage(message)`
```javascript
function showErrorMessage(message) {
    const mapLoader = document.getElementById('mapLoader');
    if (mapLoader) {
        mapLoader.innerHTML = `
            <div class="text-center">
                <i class="bi bi-exclamation-triangle display-1 text-danger mb-3"></i>
                <h5 class="text-danger">Error al cargar el mapa</h5>
                <p class="text-muted mb-3">${message}</p>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> Reintentar
                </button>
            </div>
        `;
        mapLoader.style.display = 'flex';
    }
}
```

## 🎨 Características del Loader

### Diseño
- **Posición:** Absolute sobre el mapa (z-index: 1000)
- **Fondo:** Blanco semi-transparente (75% opacidad)
- **Spinner:** Bootstrap spinner-border (3rem × 3rem)
- **Color:** Primary (azul)
- **Texto:** "Cargando ubicaciones..." en gris

### Comportamiento
1. **Se muestra automáticamente** al cargar la página
2. **Se oculta** cuando:
   - Las ubicaciones se cargan exitosamente Y
   - Hay al menos 1 ubicación para mostrar
3. **Cambia a mensaje informativo** cuando:
   - Las ubicaciones se cargan exitosamente PERO
   - No hay ninguna ubicación con coordenadas
4. **Cambia a mensaje de error** cuando:
   - Falla la petición a la API
   - Error en el servidor
   - No hay conexión

### Ventajas
✅ Mejor experiencia de usuario (UX)  
✅ Feedback visual claro del estado de carga  
✅ Manejo de errores amigable  
✅ Mensaje útil cuando no hay datos  
✅ Botón de reintento en caso de error  

## 🧪 Cómo Probar

### Caso 1: Carga Normal (Con Ubicaciones)
1. Abre el Dashboard de SIGVE
2. Deberías ver brevemente:
   - Spinner animado
   - Texto "Cargando ubicaciones..."
3. Después de 1-3 segundos:
   - El loader desaparece
   - Los marcadores aparecen en el mapa

### Caso 2: Sin Ubicaciones
1. Elimina las coordenadas de todos los talleres/cuarteles
2. Recarga el Dashboard
3. Deberías ver:
   - Icono de ubicación grande
   - "No hay ubicaciones registradas"
   - Mensaje explicativo

### Caso 3: Error de Conexión
1. Apaga el servidor Django o corta la conexión
2. Recarga el Dashboard
3. Deberías ver:
   - Icono de alerta
   - "Error al cargar el mapa"
   - Botón "Reintentar"

## 📊 Tiempos de Carga Típicos

| Escenario | Tiempo Aprox. | Experiencia |
|-----------|---------------|-------------|
| 1-5 ubicaciones | 0.5-1s | Casi instantáneo |
| 5-20 ubicaciones | 1-2s | Loader breve, fluido |
| 20-50 ubicaciones | 2-3s | Loader visible, aceptable |
| Más de 50 | 3-5s | Considerar paginación |

## 🔄 Flujo de Estados

```
┌─────────────────┐
│  Página Carga   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Muestra Loader │
│  (Spinner)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Petición API   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│ OK   │  │Error │
└──┬───┘  └───┬──┘
   │          │
   ▼          ▼
┌──────┐  ┌──────────┐
│¿Hay  │  │ Mostrar  │
│datos?│  │ Error    │
└──┬───┘  └──────────┘
   │
┌──┴──┐
│ Sí  │ No
▼     ▼
┌─────┐ ┌──────────┐
│Oculta│ │Mensaje   │
│Loader│ │"Sin      │
│      │ │datos"    │
└─────┘ └──────────┘
```

## 💡 Mejoras Futuras (Opcional)

Posibles mejoras adicionales:

1. **Skeleton Loading**
   - Mostrar placeholders de marcadores mientras carga
   
2. **Progreso Incremental**
   - "Cargando 5 de 10 ubicaciones..."
   
3. **Animaciones**
   - Fade in/out suaves con CSS transitions
   
4. **Caché**
   - Guardar ubicaciones en localStorage
   - Mostrar datos en caché mientras actualiza

5. **Lazy Loading**
   - Cargar marcadores por proximidad/viewport
   - Solo cargar visibles inicialmente

## 📖 Documentación Relacionada

- `INSTALACION_MAPA.md` - Guía de instalación
- `QUICK_START_MAPA.md` - Guía rápida
- `FIXES_MAPAS.md` - Correcciones previas
- `ARQUITECTURA_MAPAS.md` - Documentación técnica

---

**Mejora implementada:** 16 de noviembre de 2025  
**Sistema:** SIGVE - Sistema de Gestión de Vehículos de Emergencia

