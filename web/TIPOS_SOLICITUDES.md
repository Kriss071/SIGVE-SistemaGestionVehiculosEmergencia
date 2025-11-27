# Tipos de Solicitudes - SIGVE

Este documento contiene el listado de tipos de solicitudes disponibles para **talleres**, con sus respectivos esquemas de formularios en formato JSON.

> **Nota importante**: Los cuarteles de bomberos NO realizan solicitudes de datos (`data_request`) a SIGVE. Los cuarteles solo gestionan solicitudes de mantenimiento (`maintenance_request`) para enviar vehículos a talleres, lo cual es un flujo diferente y no requiere tipos de solicitud configurables.

## Estructura de un Tipo de Solicitud

Cada tipo de solicitud contiene:
- **Nombre**: Nombre descriptivo del tipo de solicitud
- **Tabla Objetivo**: Tabla de la base de datos donde se guardará la información
- **Descripción**: Explicación del propósito de la solicitud
- **Esquema del Formulario**: JSON con la definición de los campos del formulario

---

## Solicitudes para Talleres

Los talleres pueden solicitar cambios en los catálogos maestros del sistema SIGVE mediante solicitudes de datos (`data_request`). Estas solicitudes son revisadas y aprobadas por los administradores de SIGVE.

---

### 1. Solicitud de Nuevo Repuesto al Catálogo

**Nombre:** `Solicitud de Nuevo Repuesto al Catálogo`

**Tabla Objetivo:** `spare_part`

**Descripción:** Permite a los talleres solicitar la incorporación de un nuevo repuesto al catálogo maestro de SIGVE. Los talleres tienen conocimiento técnico que puede enriquecer el catálogo con repuestos especializados para vehículos de emergencia.

**Esquema del Formulario:**
```json
{
  "fields": [
    {
      "name": "name",
      "label": "Nombre del Repuesto",
      "type": "text",
      "required": true,
      "placeholder": "Ej: Filtro de Combustible",
      "help_text": "Nombre técnico y descriptivo del repuesto"
    },
    {
      "name": "sku",
      "label": "SKU Propuesto",
      "type": "text",
      "required": false,
      "placeholder": "Ej: FC-002",
      "help_text": "Código SKU sugerido basado en estándares del taller (opcional, será asignado por SIGVE si se omite)"
    },
    {
      "name": "brand",
      "label": "Marca",
      "type": "text",
      "required": false,
      "placeholder": "Ej: Bosch, Mann Filter, etc.",
      "help_text": "Marca o fabricante del repuesto"
    },
    {
      "name": "description",
      "label": "Descripción Técnica",
      "type": "textarea",
      "required": false,
      "placeholder": "Especificaciones técnicas, compatibilidad con marcas y modelos de vehículos, referencias cruzadas, etc.",
      "help_text": "Información técnica detallada del repuesto"
    },
    {
      "name": "common_vehicles",
      "label": "Vehículos Comunes de Uso",
      "type": "textarea",
      "required": false,
      "placeholder": "Ej: Carros bomba, Camionetas de rescate, etc.",
      "help_text": "Tipos de vehículos donde se utiliza comúnmente este repuesto"
    }
  ]
}
```

---

### 2. Solicitud de Nuevo Proveedor

**Nombre:** `Solicitud de Nuevo Proveedor`

**Tabla Objetivo:** `supplier`

**Descripción:** Permite a los talleres solicitar la incorporación de un nuevo proveedor al sistema. El proveedor puede ser local (asociado exclusivamente al taller) o global (disponible para todos los talleres del sistema).

**Esquema del Formulario:**
```json
{
  "fields": [
    {
      "name": "name",
      "label": "Nombre del Proveedor",
      "type": "text",
      "required": true,
      "placeholder": "Ej: Distribuidora de Repuestos Ltda.",
      "help_text": "Razón social o nombre comercial"
    },
    {
      "name": "rut",
      "label": "RUT",
      "type": "text",
      "required": false,
      "placeholder": "Ej: 76.123.456-7",
      "help_text": "RUT del proveedor"
    },
    {
      "name": "address",
      "label": "Dirección",
      "type": "text",
      "required": false,
      "placeholder": "Ej: Calle Industrial 456, Santiago",
      "help_text": "Dirección física del proveedor"
    },
    {
      "name": "phone",
      "label": "Teléfono de Contacto",
      "type": "tel",
      "required": false,
      "placeholder": "Ej: +56 2 2345 6789",
      "help_text": "Teléfono principal de contacto"
    },
    {
      "name": "email",
      "label": "Correo Electrónico",
      "type": "email",
      "required": false,
      "placeholder": "Ej: ventas@proveedor.cl",
      "help_text": "Correo para contacto comercial"
    },
    {
      "name": "supplier_type",
      "label": "Tipo de Proveedor",
      "type": "select",
      "required": true,
      "options": [
        {"value": "local", "label": "Proveedor Local (Asociado a este taller)"},
        {"value": "global", "label": "Proveedor Global (Disponible para todos)"}
      ],
      "help_text": "Seleccione si el proveedor es exclusivo del taller o global"
    },
    {
      "name": "specialties",
      "label": "Especialidades",
      "type": "textarea",
      "required": false,
      "placeholder": "Ej: Repuestos para vehículos de emergencia, filtros especializados, etc.",
      "help_text": "Tipos de productos o servicios que ofrece el proveedor"
    }
  ]
}
```

---

### 3. Solicitud de Actualización de Información de Vehículo

**Nombre:** `Solicitud de Actualización de Información de Vehículo`

**Tabla Objetivo:** `vehicle`

**Descripción:** Permite a los talleres solicitar la actualización de información técnica de vehículos que han sido atendidos. Esto incluye kilometraje actualizado, cambios en especificaciones detectados durante mantención, corrección de datos erróneos, o actualización de fechas de revisión técnica.

**Esquema del Formulario:**
```json
{
  "fields": [
    {
      "name": "license_plate",
      "label": "Patente del Vehículo",
      "type": "text",
      "required": true,
      "placeholder": "Ej: ABCD12",
      "help_text": "Patente del vehículo a actualizar"
    },
    {
      "name": "mileage",
      "label": "Kilometraje Registrado",
      "type": "number",
      "required": false,
      "placeholder": "Ej: 52000",
      "help_text": "Kilometraje actual registrado durante la mantención"
    },
    {
      "name": "engine_number",
      "label": "Número de Motor",
      "type": "text",
      "required": false,
      "placeholder": "Ej: ENG123456789",
      "help_text": "Número de motor (si se detectó corrección o actualización)"
    },
    {
      "name": "vin",
      "label": "VIN (Número de Chasis)",
      "type": "text",
      "required": false,
      "placeholder": "Ej: 1HGBH41JXMN109186",
      "help_text": "Número de identificación del vehículo"
    },
    {
      "name": "oil_capacity_liters",
      "label": "Capacidad de Aceite (Litros)",
      "type": "number",
      "required": false,
      "step": "0.1",
      "placeholder": "Ej: 5.0",
      "help_text": "Capacidad real medida durante mantención"
    },
    {
      "name": "next_revision_date",
      "label": "Próxima Revisión Técnica",
      "type": "date",
      "required": false,
      "help_text": "Fecha recomendada para próxima revisión técnica"
    },
    {
      "name": "maintenance_observations",
      "label": "Observaciones de Mantención",
      "type": "textarea",
      "required": false,
      "placeholder": "Detalle las actualizaciones o correcciones detectadas durante la mantención...",
      "help_text": "Descripción de los cambios técnicos detectados o correcciones necesarias"
    }
  ]
}
```

---

### 4. Solicitud de Nuevo Tipo de Vehículo

**Nombre:** `Solicitud de Nuevo Tipo de Vehículo`

**Tabla Objetivo:** `vehicle_type`

**Descripción:** Permite a los talleres solicitar la incorporación de un nuevo tipo de vehículo al catálogo del sistema. Esto es útil cuando se requiere categorizar un vehículo que no existe en las opciones actuales del sistema.

**Esquema del Formulario:**
```json
{
  "fields": [
    {
      "name": "name",
      "label": "Nombre del Tipo de Vehículo",
      "type": "text",
      "required": true,
      "placeholder": "Ej: Unidad de Rescate Acuático",
      "help_text": "Nombre descriptivo del tipo de vehículo"
    },
    {
      "name": "description",
      "label": "Descripción",
      "type": "textarea",
      "required": false,
      "placeholder": "Descripción detallada del tipo de vehículo, características principales, uso específico, etc.",
      "help_text": "Información detallada sobre este tipo de vehículo"
    },
    {
      "name": "justification",
      "label": "Justificación",
      "type": "textarea",
      "required": true,
      "placeholder": "Explique por qué es necesario agregar este nuevo tipo de vehículo al sistema...",
      "help_text": "Razón por la cual se requiere este nuevo tipo de vehículo"
    }
  ]
}
```

---

### 5. Solicitud de Nuevo Estado de Vehículo

**Nombre:** `Solicitud de Nuevo Estado de Vehículo`

**Tabla Objetivo:** `vehicle_status`

**Descripción:** Permite a los talleres solicitar la incorporación de un nuevo estado para vehículos cuando los estados actuales no cubren una situación específica que se presenta frecuentemente en el trabajo del taller.

**Esquema del Formulario:**
```json
{
  "fields": [
    {
      "name": "name",
      "label": "Nombre del Estado",
      "type": "text",
      "required": true,
      "placeholder": "Ej: En Inspección, Fuera de Servicio Temporal",
      "help_text": "Nombre descriptivo del nuevo estado"
    },
    {
      "name": "description",
      "label": "Descripción",
      "type": "textarea",
      "required": false,
      "placeholder": "Descripción detallada del estado, cuándo se aplica, duración esperada, etc.",
      "help_text": "Información sobre cuándo y cómo se usa este estado"
    },
    {
      "name": "justification",
      "label": "Justificación",
      "type": "textarea",
      "required": true,
      "placeholder": "Explique por qué los estados actuales no cubren esta situación...",
      "help_text": "Razón por la cual se requiere este nuevo estado"
    }
  ]
}
```

---

## Notas sobre los Esquemas de Formulario

### Tipos de Campo Disponibles

- **text**: Campo de texto simple
- **textarea**: Campo de texto multilínea
- **number**: Campo numérico
- **email**: Campo de correo electrónico con validación
- **tel**: Campo de teléfono
- **date**: Campo de fecha
- **select**: Campo de selección con opciones predefinidas

### Propiedades de los Campos

- **name**: Nombre del campo (debe coincidir con el nombre de la columna en la base de datos)
- **label**: Etiqueta visible para el usuario
- **type**: Tipo de campo del formulario
- **required**: Indica si el campo es obligatorio (true/false)
- **placeholder**: Texto de ejemplo que aparece en el campo
- **help_text**: Texto de ayuda que aparece debajo del campo
- **step**: Para campos numéricos, define el incremento (opcional)
- **options**: Para campos select, array de opciones con value y label

### Proceso de Aprobación

1. El usuario del taller completa el formulario y envía la solicitud
2. La solicitud queda en estado "pendiente" en el sistema
3. Un administrador SIGVE revisa la solicitud en el Centro de Solicitudes
4. El administrador puede:
   - **Aprobar**: Los datos se crean/actualizan automáticamente en la tabla objetivo
   - **Rechazar**: Se envía un mensaje al solicitante explicando el motivo del rechazo
   - **Editar y Aprobar**: El administrador puede modificar los datos antes de aprobar la solicitud

---

## Cómo Usar Este Documento

Para crear un nuevo tipo de solicitud en el sistema:

1. Copie uno de los esquemas JSON de ejemplo de este documento
2. Ajuste los campos según las necesidades específicas
3. Acceda a la sección "Tipos de Solicitudes" en el panel de administración SIGVE
4. Cree un nuevo tipo de solicitud usando el formulario
5. Pegue el esquema JSON en el campo "Esquema del Formulario"
6. Guarde el tipo de solicitud

Los usuarios de talleres podrán entonces seleccionar este nuevo tipo de solicitud al crear una solicitud a SIGVE desde su panel de control.

---

## Diferencias entre Solicitudes de Cuarteles y Talleres

### Cuarteles (Fire Stations)
- **NO realizan solicitudes de datos (`data_request`)** a SIGVE
- Solo gestionan **solicitudes de mantenimiento (`maintenance_request`)** para enviar vehículos a talleres
- Las solicitudes de mantenimiento son un flujo operativo diferente y no requieren tipos de solicitud configurables
- Gestionan directamente sus vehículos y usuarios del cuartel

### Talleres (Workshops)
- **SÍ realizan solicitudes de datos (`data_request`)** a SIGVE
- Solicitan cambios en catálogos maestros (repuestos, proveedores, tipos de vehículos, etc.)
- Estas solicitudes requieren aprobación de administradores SIGVE
- Los tipos de solicitud de este documento son exclusivamente para talleres
