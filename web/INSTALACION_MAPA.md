# Instalación del Sistema de Mapas en SIGVE

Este documento describe cómo instalar y configurar el sistema de mapas para visualizar ubicaciones de talleres y cuarteles en el Dashboard de SIGVE.

## 🗺️ Características Implementadas

- **Mapa interactivo** en el dashboard usando Leaflet.js (librería gratuita de OpenStreetMap)
- **Geocodificación automática** de direcciones al crear/editar talleres y cuarteles
- **Marcadores diferenciados** para talleres (azul con icono de llave) y cuarteles (rojo con icono de fuego)
- **Filtros interactivos** para mostrar/ocultar capas de talleres y cuarteles
- **Popups informativos** con detalles de cada ubicación

## 📋 Pasos de Instalación

### 1. Ejecutar la Migración de Base de Datos en Supabase

El primer paso es agregar las columnas de latitud y longitud a las tablas `workshop` y `fire_station` en Supabase.

1. Abre el **SQL Editor** en tu proyecto de Supabase
2. Ejecuta el script ubicado en: `database/migrations/add_location_coordinates.sql`

```sql
-- El script agregará:
-- - Columnas latitude y longitude a workshop
-- - Columnas latitude y longitude a fire_station
-- - Índices para mejorar el rendimiento
```

### 2. Verificar la Configuración

Una vez ejecutada la migración, verifica que los cambios se aplicaron correctamente:

```sql
-- Verificar estructura de workshop
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'workshop';

-- Verificar estructura de fire_station
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'fire_station';
```

Deberías ver las columnas `latitude` y `longitude` en ambas tablas.

### 3. No se Requiere Instalación de Dependencias Adicionales

El sistema utiliza:
- **Leaflet.js**: cargado desde CDN (ya incluido en el template)
- **Nominatim (OpenStreetMap)**: API de geocodificación gratuita (no requiere API key)

## 🎯 Cómo Usar el Sistema

### Agregar Ubicaciones a Talleres y Cuarteles

1. **Desde el Dashboard**, haz clic en "Crear Taller" o "Crear Cuartel"
2. Ingresa la dirección completa (ej: "Av. Libertador Bernardo O'Higgins 1234, Santiago, Chile")
3. Haz clic en el botón **"🔍 Buscar ubicación"** que aparece debajo del campo de dirección
4. El sistema buscará automáticamente las coordenadas y las guardará

> **Nota**: Para mejores resultados, ingresa direcciones completas incluyendo número, calle, ciudad y país (Chile).

### Ver el Mapa

1. Ve al **Dashboard de SIGVE**
2. Desplázate hasta la sección **"Mapa de Ubicaciones"**
3. El mapa mostrará automáticamente todos los talleres y cuarteles que tengan coordenadas registradas
4. Usa los botones de filtro para mostrar/ocultar talleres o cuarteles
5. Haz clic en los marcadores para ver información detallada

### Actualizar Ubicaciones Existentes

Para talleres y cuarteles ya registrados sin coordenadas:

1. Edita el taller/cuartel desde su respectiva lista o desde el dashboard
2. Verifica o actualiza la dirección
3. Haz clic en "Buscar ubicación"
4. Guarda los cambios

## 🔧 Estructura de Archivos Modificados/Creados

### Archivos Nuevos
```
database/migrations/add_location_coordinates.sql  # Migración SQL
apps/sigve/static/js/geocoding.js                # Módulo de geocodificación
INSTALACION_MAPA.md                              # Este archivo
```

### Archivos Modificados
```
apps/sigve/forms.py                              # Formularios con campos de coordenadas
apps/sigve/views.py                              # Vistas y API endpoints
apps/sigve/urls.py                               # Ruta para API de ubicaciones
apps/sigve/templates/sigve/dashboard.html        # Template con mapa
apps/sigve/static/js/dashboard.js                # Inicialización del mapa
apps/sigve/static/js/workshop.js                 # Geocodificación en modal de taller
apps/sigve/static/js/fire_station.js             # Geocodificación en modal de cuartel
```

## 🌍 Sobre la Geocodificación

### API Utilizada: Nominatim (OpenStreetMap)

- **Gratuita**: No requiere API key
- **Limitaciones**: Máximo 1 petición por segundo (implementado automáticamente)
- **Cobertura**: Mundial, con buena cobertura en Chile

### Consejos para Mejores Resultados

1. **Direcciones completas**: Incluye número, calle, comuna, ciudad y "Chile"
2. **Formato**: "Calle Número, Comuna, Ciudad, Chile"
3. **Ejemplos**:
   - ✅ "Av. Libertador Bernardo O'Higgins 1234, Santiago, Chile"
   - ✅ "Calle Las Hortensias 567, Providencia, Santiago, Chile"
   - ❌ "Las Hortensias 567" (muy genérico)

### Geocodificación Manual

Si la búsqueda automática no encuentra la ubicación:

1. Busca la dirección en [OpenStreetMap](https://www.openstreetmap.org/)
2. Haz clic derecho en el lugar exacto
3. Copia las coordenadas (latitud, longitud)
4. Ingresa manualmente usando las herramientas de desarrollo del navegador:
   ```javascript
   document.getElementById('workshop-latitude').value = '-33.4489';
   document.getElementById('workshop-longitude').value = '-70.6693';
   ```

## 📊 API Endpoint

### GET /sigve/api/map-locations/

Devuelve todas las ubicaciones de talleres y cuarteles con coordenadas.

**Respuesta**:
```json
{
  "success": true,
  "locations": {
    "workshops": [
      {
        "id": 1,
        "name": "Taller Central",
        "address": "Av. Principal 123",
        "latitude": -33.4489,
        "longitude": -70.6693,
        "phone": "+56912345678",
        "email": "contacto@taller.cl"
      }
    ],
    "fire_stations": [
      {
        "id": 1,
        "name": "Primera Compañía",
        "address": "Calle Bomberos 456",
        "latitude": -33.4372,
        "longitude": -70.6506,
        "commune": "Santiago"
      }
    ]
  }
}
```

## 🐛 Solución de Problemas

### El mapa no se muestra

1. Verifica que ejecutaste la migración SQL en Supabase
2. Revisa la consola del navegador (F12) para errores
3. Asegúrate de que los archivos JavaScript estén cargando correctamente

### La geocodificación no funciona

1. Verifica la conexión a internet
2. Revisa que la dirección esté bien escrita y sea específica
3. Intenta agregar más detalles (comuna, ciudad, país)
4. Si persiste, ingresa las coordenadas manualmente

### No aparecen ubicaciones en el mapa

1. Verifica que los talleres/cuarteles tengan coordenadas (latitud y longitud) en la base de datos
2. Revisa la consola del navegador para errores en la API
3. Asegúrate de que los filtros de capas estén activados

## 📝 Notas Adicionales

- Las coordenadas se guardan automáticamente al usar el botón "Buscar ubicación"
- Los campos de latitud y longitud son opcionales
- El mapa ajusta automáticamente el zoom para mostrar todas las ubicaciones
- Los iconos de marcadores usan Bootstrap Icons (ya incluidos en el proyecto)

## 🔄 Próximas Mejoras (Opcionales)

Posibles mejoras futuras:
- Integración con Google Maps para geocodificación más precisa
- Cálculo de rutas entre ubicaciones
- Búsqueda de ubicaciones cercanas
- Agrupamiento de marcadores en niveles de zoom bajos
- Exportación de ubicaciones a KML/GPX

---

**Desarrollado para SIGVE** - Sistema de Gestión de Vehículos de Emergencia

