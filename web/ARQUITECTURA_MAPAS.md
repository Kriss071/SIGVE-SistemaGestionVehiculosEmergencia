# Arquitectura del Sistema de Mapas - SIGVE

## 📐 Visión General

El sistema de mapas de SIGVE está diseñado siguiendo una arquitectura cliente-servidor con las siguientes capas:

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Cliente)                 │
├─────────────────────────────────────────────────────┤
│  • Leaflet.js (Renderizado de mapas)               │
│  • geocoding.js (Geocodificación de direcciones)    │
│  • dashboard.js (Gestión de marcadores)             │
└─────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────┐
│              Backend (Django/Python)                 │
├─────────────────────────────────────────────────────┤
│  • Views (Lógica de negocio)                        │
│  • Forms (Validación de datos)                      │
│  • Services (Interacción con Supabase)              │
└─────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────┐
│            Base de Datos (Supabase)                  │
├─────────────────────────────────────────────────────┤
│  • Tabla workshop (latitude, longitude)             │
│  • Tabla fire_station (latitude, longitude)         │
└─────────────────────────────────────────────────────┘
```

## 🔧 Componentes del Sistema

### 1. Base de Datos (Supabase)

#### Tabla: `workshop`
```sql
CREATE TABLE workshop (
    id integer PRIMARY KEY,
    name varchar NOT NULL,
    address varchar UNIQUE,
    phone varchar UNIQUE,
    email varchar UNIQUE,
    latitude decimal(10, 8),      -- Nueva columna
    longitude decimal(11, 8),     -- Nueva columna
    created_at timestamp NOT NULL,
    updated_at timestamp
);

CREATE INDEX idx_workshop_coordinates ON workshop(latitude, longitude);
```

#### Tabla: `fire_station`
```sql
CREATE TABLE fire_station (
    id integer PRIMARY KEY,
    name varchar NOT NULL UNIQUE,
    address varchar NOT NULL UNIQUE,
    commune_id integer REFERENCES commune(id),
    latitude decimal(10, 8),      -- Nueva columna
    longitude decimal(11, 8),     -- Nueva columna
    created_at timestamp NOT NULL,
    updated_at timestamp
);

CREATE INDEX idx_fire_station_coordinates ON fire_station(latitude, longitude);
```

### 2. Backend (Django)

#### Formularios (`apps/sigve/forms.py`)

```python
class WorkshopForm(forms.Form):
    name = forms.CharField(...)
    address = forms.CharField(...)
    latitude = forms.DecimalField(max_digits=10, decimal_places=8, required=False, 
                                  widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=11, decimal_places=8, required=False,
                                   widget=forms.HiddenInput())
    phone = forms.CharField(...)
    email = forms.EmailField(...)

class FireStationForm(forms.Form):
    name = forms.CharField(...)
    address = forms.CharField(...)
    latitude = forms.DecimalField(max_digits=10, decimal_places=8, required=False,
                                  widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=11, decimal_places=8, required=False,
                                   widget=forms.HiddenInput())
    commune_id = forms.IntegerField(...)
```

#### API Endpoint (`apps/sigve/views.py`)

```python
@require_supabase_login
@require_role("Admin SIGVE")
def api_get_map_locations(request):
    """
    Retorna las ubicaciones de todos los talleres y cuarteles.
    
    Response:
    {
        "success": true,
        "locations": {
            "workshops": [...],
            "fire_stations": [...]
        }
    }
    """
    workshops = WorkshopService.get_all_workshops()
    fire_stations = FireStationService.get_all_fire_stations()
    
    # Formatear y filtrar solo los que tienen coordenadas
    return JsonResponse({
        'success': True,
        'locations': process_locations(workshops, fire_stations)
    })
```

### 3. Frontend (JavaScript)

#### Módulo de Geocodificación (`geocoding.js`)

```javascript
const Geocoding = {
    NOMINATIM_URL: 'https://nominatim.openstreetmap.org/search',
    
    async geocodeAddress(address) {
        // Convierte una dirección en coordenadas
        // Implementa rate limiting (1 petición/segundo)
        // Retorna {lat, lon} o null
    },
    
    setupAddressGeocoding(addressInputId, latInputId, lonInputId) {
        // Configura la geocodificación automática para un formulario
        // Crea botón "Buscar ubicación"
        // Muestra indicadores visuales
    }
};
```

#### Gestión del Mapa (`dashboard.js`)

```javascript
// Variables globales
let map = null;
let workshopMarkers = [];
let fireStationMarkers = [];

// Inicialización
function initializeMap() {
    // Crea el mapa centrado en Santiago
    map = L.map('map').setView([-33.4489, -70.6693], 11);
    
    // Agrega capa de tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Carga ubicaciones
    loadMapLocations();
}

// Carga de ubicaciones
function loadMapLocations() {
    fetch('/sigve/api/map-locations/')
        .then(response => response.json())
        .then(data => {
            data.locations.workshops.forEach(addWorkshopMarker);
            data.locations.fire_stations.forEach(addFireStationMarker);
            fitMapBounds();
        });
}

// Creación de marcadores
function addWorkshopMarker(workshop) {
    const icon = L.divIcon({
        html: '<div style="..."><i class="bi bi-wrench"></i></div>',
        iconSize: [30, 30]
    });
    
    const marker = L.marker([workshop.latitude, workshop.longitude], { icon })
        .bindPopup(createWorkshopPopup(workshop))
        .addTo(map);
    
    workshopMarkers.push(marker);
}
```

## 🔄 Flujo de Datos

### Flujo de Creación de Ubicación

```
1. Usuario abre modal de "Crear Taller"
   └─> workshop.js: setupCreateMode()
       └─> setupGeocoding() inicializa el botón de geocodificación

2. Usuario ingresa dirección y hace clic en "Buscar ubicación"
   └─> geocoding.js: geocodeAddress()
       └─> Petición a Nominatim API
           └─> Coordenadas se guardan en campos ocultos

3. Usuario guarda el formulario
   └─> views.py: workshop_create()
       └─> WorkshopForm.cleaned_data incluye latitude y longitude
           └─> WorkshopService.create_workshop(data)
               └─> Supabase: INSERT con coordenadas

4. Dashboard se recarga
   └─> dashboard.js: initializeMap()
       └─> loadMapLocations()
           └─> API: /sigve/api/map-locations/
               └─> Nuevo marcador aparece en el mapa
```

### Flujo de Edición de Ubicación

```
1. Usuario hace clic en "Editar Taller" en el mapa o lista
   └─> workshop.js: open('edit', workshopId)
       └─> loadWorkshopData()
           └─> API: /sigve/api/workshops/{id}/
               └─> populateForm() llena campos incluyendo coordenadas

2. Usuario modifica dirección y busca nueva ubicación
   └─> geocoding.js: geocodeAddress()
       └─> Nuevas coordenadas en campos ocultos

3. Usuario guarda cambios
   └─> views.py: workshop_edit()
       └─> WorkshopService.update_workshop()
           └─> Supabase: UPDATE con nuevas coordenadas

4. Dashboard se actualiza
   └─> Marcador se mueve a nueva ubicación
```

## 🌐 Integración con APIs Externas

### Nominatim (OpenStreetMap)

**Características:**
- API REST pública y gratuita
- No requiere API key
- Cobertura mundial
- Rate limit: 1 petición/segundo

**Endpoint:**
```
GET https://nominatim.openstreetmap.org/search
    ?q={dirección}
    &format=json
    &limit=1
    &countrycodes=cl
    &addressdetails=1
```

**Response:**
```json
[
    {
        "lat": "-33.4489",
        "lon": "-70.6693",
        "display_name": "Av. Libertador...",
        "address": {
            "road": "Avenida Libertador Bernardo O'Higgins",
            "city": "Santiago",
            "country": "Chile"
        }
    }
]
```

**Limitaciones Implementadas:**
```javascript
// Rate limiting en geocoding.js
const DELAY_MS = 1000;
let lastRequestTime = 0;

async geocodeAddress(address) {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < DELAY_MS) {
        await this.sleep(DELAY_MS - timeSinceLastRequest);
    }
    
    this.lastRequestTime = Date.now();
    // ... realizar petición
}
```

### Leaflet.js

**Características:**
- Librería JavaScript open-source
- 42 KB comprimida
- Compatible con todos los navegadores modernos
- Extensible con plugins

**Inicialización:**
```javascript
// Crear mapa
const map = L.map('map').setView([lat, lon], zoom);

// Agregar capa de tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
```

**Marcadores Personalizados:**
```javascript
const customIcon = L.divIcon({
    className: 'custom-map-marker',
    html: '<div style="...">...</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});

L.marker([lat, lon], { icon: customIcon })
    .bindPopup('<div>...</div>')
    .addTo(map);
```

## 🎨 Interfaz de Usuario

### Elementos Visuales

#### Marcadores

**Talleres (Azul):**
- Color: `#0d6efd` (Bootstrap primary)
- Icono: Bootstrap Icon `bi-wrench`
- Tamaño: 30x30px
- Borde: 3px blanco con sombra

**Cuarteles (Rojo):**
- Color: `#dc3545` (Bootstrap danger)
- Icono: Bootstrap Icon `bi-fire`
- Tamaño: 30x30px
- Borde: 3px blanco con sombra

#### Popups

Estructura del popup:
```html
<div style="min-width: 200px;">
    <h6 class="mb-2">
        <i class="bi bi-wrench text-primary"></i>
        Nombre del Taller
    </h6>
    <p class="mb-1 small">
        <strong>Dirección:</strong> Av. Principal 123
    </p>
    <p class="mb-1 small">
        <strong>Teléfono:</strong> +56912345678
    </p>
    <p class="mb-0 small">
        <strong>Email:</strong> contacto@taller.cl
    </p>
</div>
```

#### Controles del Mapa

```html
<div class="btn-group btn-group-sm" role="group">
    <input type="checkbox" class="btn-check" id="toggle-workshops" checked>
    <label class="btn btn-outline-primary" for="toggle-workshops">
        <i class="bi bi-wrench"></i> Talleres
    </label>
    
    <input type="checkbox" class="btn-check" id="toggle-fire-stations" checked>
    <label class="btn btn-outline-danger" for="toggle-fire-stations">
        <i class="bi bi-fire"></i> Cuarteles
    </label>
</div>
```

## 🔒 Seguridad

### Autenticación y Autorización

```python
@require_supabase_login
@require_role("Admin SIGVE")
def api_get_map_locations(request):
    # Solo usuarios con rol "Admin SIGVE" pueden acceder
    ...
```

### Validación de Datos

**Backend:**
```python
class WorkshopForm(forms.Form):
    latitude = forms.DecimalField(
        max_digits=10,
        decimal_places=8,
        required=False
    )
    # Rango válido: -90 a 90
    
    longitude = forms.DecimalField(
        max_digits=11,
        decimal_places=8,
        required=False
    )
    # Rango válido: -180 a 180
```

**Base de Datos:**
```sql
ALTER TABLE workshop
ADD COLUMN latitude DECIMAL(10, 8),
ADD COLUMN longitude DECIMAL(11, 8);

-- Limitar a rango válido (opcional)
ALTER TABLE workshop
ADD CONSTRAINT check_latitude CHECK (latitude >= -90 AND latitude <= 90),
ADD CONSTRAINT check_longitude CHECK (longitude >= -180 AND longitude <= 180);
```

## 🚀 Optimizaciones

### Performance

1. **Índices en Base de Datos:**
```sql
CREATE INDEX idx_workshop_coordinates ON workshop(latitude, longitude);
CREATE INDEX idx_fire_station_coordinates ON fire_station(latitude, longitude);
```

2. **Carga Asíncrona:**
```javascript
// El mapa se carga después del DOM
document.addEventListener('DOMContentLoaded', initializeMap);

// Las ubicaciones se cargan mediante fetch asíncrono
async function loadMapLocations() {
    const response = await fetch('/sigve/api/map-locations/');
    // ...
}
```

3. **Filtrado en Backend:**
```python
# Solo enviar ubicaciones con coordenadas
if workshop.get('latitude') and workshop.get('longitude'):
    locations['workshops'].append({...})
```

### Escalabilidad

**Estrategias futuras para muchas ubicaciones:**

1. **Clustering de Marcadores:**
```javascript
// Usar plugin Leaflet.markercluster
const markers = L.markerClusterGroup();
markers.addLayer(L.marker([lat, lon]));
map.addLayer(markers);
```

2. **Paginación de API:**
```python
def api_get_map_locations(request):
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 100)
    
    workshops = WorkshopService.get_all_workshops()
    paginated = workshops[(page-1)*limit:page*limit]
    # ...
```

3. **Caché:**
```python
from django.core.cache import cache

def api_get_map_locations(request):
    cache_key = 'map_locations'
    data = cache.get(cache_key)
    
    if not data:
        # Calcular datos
        cache.set(cache_key, data, timeout=300)  # 5 minutos
    
    return JsonResponse(data)
```

## 📱 Responsive Design

El mapa se adapta automáticamente a diferentes tamaños de pantalla:

```css
#map {
    height: 500px;
    width: 100%;
}

@media (max-width: 768px) {
    #map {
        height: 350px;
    }
}
```

Leaflet también maneja automáticamente:
- Touch gestures en móviles
- Zoom mediante pinch
- Controles táctiles

## 🧪 Testing

### Tests Recomendados

**Backend:**
```python
def test_api_map_locations_requires_auth():
    """Verifica que la API requiere autenticación"""
    response = client.get('/sigve/api/map-locations/')
    assert response.status_code == 302  # Redirect a login

def test_workshop_with_coordinates():
    """Verifica que se guardan las coordenadas"""
    data = {
        'name': 'Taller Test',
        'address': 'Dirección Test',
        'latitude': -33.4489,
        'longitude': -70.6693
    }
    workshop = WorkshopService.create_workshop(data)
    assert workshop['latitude'] == -33.4489
```

**Frontend:**
```javascript
describe('Geocoding', () => {
    it('should geocode a valid address', async () => {
        const coords = await Geocoding.geocodeAddress(
            'Av. Libertador Bernardo O\'Higgins 1234, Santiago, Chile'
        );
        expect(coords).not.toBeNull();
        expect(coords.lat).toBeCloseTo(-33.44, 1);
        expect(coords.lon).toBeCloseTo(-70.66, 1);
    });
});
```

---

**Documentado para SIGVE** - Sistema de Gestión de Vehículos de Emergencia

