# Fire Station - Aplicación de Gestión de Cuartel de Bomberos

## Descripción

La aplicación **Fire Station** permite a los cuarteles de bomberos gestionar sus vehículos y usuarios asignados al cuartel.

## Características

### Dashboard
- Vista general de estadísticas de vehículos
- Contadores de vehículos por estado (Disponible, En Mantención, De Baja)
- Gráfico de vehículos por tipo
- Listado de vehículos recientes

### Gestión de Vehículos
- Listado completo de vehículos del cuartel
- Filtros por estado, tipo y patente
- Creación de nuevos vehículos (solo Jefe de Cuartel)
- Edición de vehículos existentes (solo Jefe de Cuartel)
- Visualización detallada de vehículos
- Eliminación de vehículos (solo Jefe de Cuartel)

**Campos editables después de crear el vehículo:**
- Marca, modelo, año
- Tipo de vehículo
- Estado del vehículo
- Kilometraje
- Capacidad de aceite
- Fechas de inscripción y próxima revisión
- Tipos de combustible, transmisión, aceite y refrigerante

**Campos NO editables después de crear:**
- Patente (license_plate)
- Número de motor (engine_number)
- Número de chasis/VIN (vin)

### Gestión de Usuarios
- Listado de usuarios del cuartel (solo Jefe de Cuartel)
- Edición de perfiles de usuarios
- Activación/desactivación de usuarios
- Asignación de roles

## Permisos

### Jefe de Cuartel
- Acceso completo a todas las funciones
- Puede crear, editar y eliminar vehículos
- Puede gestionar usuarios del cuartel

### Usuarios de Cuartel
- Pueden ver el dashboard
- Pueden ver la lista de vehículos
- Pueden ver detalles de vehículos
- No pueden crear, editar ni eliminar

## Estructura de Archivos

```
apps/fire_station/
├── services/
│   ├── base_service.py          # Servicio base para Supabase
│   ├── dashboard_service.py     # Lógica de dashboard
│   ├── vehicle_service.py       # Lógica de vehículos
│   └── user_service.py          # Lógica de usuarios
├── templates/fire_station/
│   ├── base.html                # Plantilla base
│   ├── dashboard.html           # Vista de dashboard
│   ├── vehicles_list.html       # Lista de vehículos
│   ├── users_list.html          # Lista de usuarios
│   ├── components/
│   │   └── navbar.html          # Barra de navegación
│   └── modals/
│       ├── vehicle_modal.html   # Modal de vehículos
│       ├── user_modal.html      # Modal de usuarios
│       └── confirmation_modal.html # Modal de confirmación
├── static/
│   ├── css/
│   │   ├── dashboard.css
│   │   ├── vehicles_list.css
│   │   └── users_list.css
│   └── js/
│       ├── dashboard.js
│       ├── vehicles_list.js
│       ├── users_list.js
│       └── modal.js
├── decorators.py                # Decoradores de autenticación
├── forms.py                     # Formularios de Django
├── views.py                     # Vistas de Django
├── urls.py                      # Rutas de la aplicación
└── models.py                    # Sin modelos (usa Supabase)
```

## URLs

- `/fire-station/` - Dashboard
- `/fire-station/vehicles/` - Lista de vehículos
- `/fire-station/users/` - Lista de usuarios (solo Jefe)
- `/fire-station/api/vehicles/<id>/` - API de vehículo
- `/fire-station/api/users/<id>/` - API de usuario

## Base de Datos

La aplicación utiliza las siguientes tablas de Supabase:

- `vehicle` - Información de vehículos
- `vehicle_type` - Tipos de vehículos
- `vehicle_status` - Estados de vehículos
- `vehicle_status_log` - Historial de cambios de estado
- `fuel_type` - Tipos de combustible
- `transmission_type` - Tipos de transmisión
- `oil_type` - Tipos de aceite
- `coolant_type` - Tipos de refrigerante
- `user_profile` - Perfiles de usuarios
- `role` - Roles de usuarios
- `fire_station` - Información del cuartel

## Uso

### Autenticación

La aplicación utiliza los decoradores `@require_supabase_login` y `@require_fire_station_user` para verificar que el usuario esté autenticado y pertenezca a un cuartel.

### Sesión

Los datos de sesión necesarios:
- `sb_user_id` - ID del usuario autenticado
- `fire_station_id` - ID del cuartel al que pertenece
- `fire_station_name` - Nombre del cuartel
- `role_name` - Nombre del rol del usuario

## Desarrollo

### Agregar nuevas funcionalidades

1. Crear servicio en `services/`
2. Crear vista en `views.py`
3. Agregar ruta en `urls.py`
4. Crear template en `templates/fire_station/`
5. Agregar estilos en `static/css/`
6. Agregar lógica JS en `static/js/`

## Tecnologías

- Django 5.2.6
- Bootstrap 5
- JavaScript ES6+
- Supabase (PostgreSQL)
- Bootstrap Icons

