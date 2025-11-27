# RESUMEN EJECUTIVO
## SIGVE - Sistema de Gestión de Vehículos de Emergencia

---

## 1. VISIÓN GENERAL

**SIGVE** es una plataforma integral diseñada para gestionar de manera centralizada y eficiente la flota de vehículos de emergencia (bomberos, ambulancias, etc.), sus procesos de mantenimiento, inventarios de repuestos y la coordinación entre cuarteles de bomberos y talleres mecánicos.

La solución digitaliza completamente el ciclo de vida de los vehículos de emergencia, desde su registro inicial hasta el seguimiento de mantenimientos, garantizando que la flota esté siempre operativa y disponible para responder a emergencias.

---

## 2. ARQUITECTURA DE LA SOLUCIÓN

La aplicación está estructurada en **tres módulos principales**, cada uno con su propio panel de control y funcionalidades específicas:

### 2.1. **Panel de Administración SIGVE** (Nivel Central)
- **Audiencia**: Administradores centrales del sistema
- **Propósito**: Gestión y supervisión global de toda la operación
- **Acceso**: Roles de Super Admin y Admin SIGVE

### 2.2. **Módulo de Taller** (Nivel Operativo - Mantenimiento)
- **Audiencia**: Administradores de taller y mecánicos
- **Propósito**: Gestión de órdenes de mantenimiento, inventario y recursos del taller
- **Acceso**: Roles de Admin Taller y Mecánico

### 2.3. **Módulo de Cuartel de Bomberos** (Nivel Operativo - Operaciones)
- **Audiencia**: Jefes de cuartel y personal operativo
- **Propósito**: Gestión de la flota del cuartel y solicitudes de mantenimiento
- **Acceso**: Rol de Jefe Cuartel

---

## 3. ROLES Y PERMISOS

El sistema implementa un modelo de roles jerárquico que garantiza la seguridad y el control de acceso:

| Rol | Descripción | Accesos Principales |
|-----|-------------|---------------------|
| **Super Admin** | Administrador máximo del sistema | Acceso completo a todos los módulos y funcionalidades |
| **Admin SIGVE** | Administrador central | Panel SIGVE completo, gestión de catálogos, aprobación de solicitudes |
| **Admin Taller** | Administrador de taller | Gestión completa del taller, empleados, inventario y órdenes |
| **Mecánico** | Operador de taller | Gestión de órdenes de mantenimiento, tareas y uso de repuestos |
| **Jefe Cuartel** | Administrador de cuartel | Gestión de vehículos del cuartel, usuarios y solicitudes de mantenimiento |

**Características de Seguridad:**
- Autenticación centralizada mediante Supabase
- Redirección automática según rol al iniciar sesión
- Control de acceso granular por módulo y funcionalidad
- Asignación de usuarios a talleres y cuarteles específicos

---

## 4. FUNCIONALIDADES PRINCIPALES

### 4.1. **Gestión de Vehículos**

**En Cuarteles:**
- Registro completo de vehículos con información técnica detallada:
  - Datos básicos: patente, marca, modelo, año, tipo de vehículo
  - Especificaciones técnicas: tipo de combustible, transmisión, aceite, refrigerante
  - Asignación a cuartel específico
  - Estado operativo del vehículo
- Visualización del historial completo de cada vehículo
- Seguimiento de cambios de estado (Disponible, En Taller, De Baja, etc.)
- Consulta de vehículos por tipo y estado

**En Talleres:**
- Búsqueda de vehículos por patente
- Creación de vehículos nuevos cuando no existen en el sistema
- Visualización de vehículos asociados a órdenes de mantenimiento

**Estados de Vehículos:**
El sistema gestiona automáticamente los estados de los vehículos:
- **Disponible**: Vehículo operativo y listo para uso
- **En Taller**: Vehículo en proceso de mantenimiento
- **De Baja**: Vehículo fuera de servicio permanente
- Los cambios de estado se registran automáticamente en un historial con usuario, fecha y razón

### 4.2. **Gestión de Órdenes de Mantenimiento**

**Proceso Completo:**
1. **Creación de Orden**: El taller crea una orden asociada a un vehículo
   - Registro de fecha de ingreso, kilometraje, tipo de mantenimiento
   - Asignación de mecánico responsable
   - Estado inicial de la orden

2. **Gestión de Tareas**: Cada orden puede contener múltiples tareas
   - Registro de tareas específicas a realizar
   - Tipos de tareas configurables (cambio de aceite, revisión de frenos, etc.)
   - Asignación de repuestos a cada tarea

3. **Control de Repuestos**: 
   - Asociación de repuestos del inventario a las tareas
   - Descuento automático del inventario al usar repuestos
   - Registro de costos por repuesto utilizado

4. **Estados de Orden**:
   - **Pendiente**: Orden creada, esperando inicio de trabajo
   - **En Taller**: Trabajo en progreso
   - **En Espera de Repuestos**: Pausada por falta de repuestos
   - **Completada**: Mantenimiento finalizado
   - Al completarse, el vehículo se marca automáticamente como "Disponible"

5. **Finalización**: 
   - Registro de fecha de salida
   - Observaciones y notas finales
   - Cálculo automático de costos totales

### 4.3. **Sistema de Solicitudes**

**Dos Tipos de Solicitudes:**

**A) Solicitudes de Mantenimiento (Cuartel → Taller)**
- Los cuarteles pueden crear solicitudes de mantenimiento para sus vehículos
- Incluyen: vehículo, tipo de solicitud, descripción del problema
- Estados: Pendiente, Aprobada, Rechazada, Cancelada
- Permiten coordinar el ingreso de vehículos al taller

**B) Solicitudes de Datos (Taller → SIGVE)**
- Los talleres pueden solicitar la creación de registros maestros
- Tipos configurables: solicitar nuevos repuestos, proveedores, tipos de vehículo, etc.
- Sistema de formularios dinámicos basado en esquemas configurables
- Proceso de aprobación/rechazo por parte de SIGVE
- Al aprobar, el sistema puede crear automáticamente el registro solicitado

**Centro de Solicitudes (SIGVE):**
- Vista centralizada de todas las solicitudes pendientes
- Filtrado por estado y tipo
- Aprobación con posibilidad de editar datos antes de crear el registro
- Rechazo con notas explicativas

### 4.4. **Gestión de Inventario de Repuestos**

**Características:**
- **Catálogo Maestro**: SIGVE mantiene un catálogo centralizado de todos los repuestos disponibles
- **Inventario por Taller**: Cada taller mantiene su propio inventario basado en el catálogo maestro
- **Control de Stock**:
  - Cantidad disponible
  - Costo actual por unidad
  - Ubicación física en el taller
  - SKU interno del taller
  - Proveedor asociado
- **Alertas de Stock Bajo**: El sistema identifica automáticamente repuestos con stock bajo (menos de 5 unidades)
- **Descuento Automático**: Al usar repuestos en una orden, se descuenta automáticamente del inventario
- **Historial de Movimientos**: Registro de entradas y salidas de inventario

### 4.5. **Gestión de Proveedores**

**En SIGVE:**
- Catálogo maestro de proveedores
- Información completa: nombre, contacto, dirección, datos de facturación

**En Talleres:**
- Asociación de proveedores locales al inventario
- Gestión de proveedores preferidos por taller

### 4.6. **Gestión de Usuarios**

**En SIGVE:**
- Gestión centralizada de todos los usuarios del sistema
- Asignación de roles
- Asignación a talleres o cuarteles específicos
- Activación/desactivación de cuentas
- Creación y edición de perfiles

**En Cuarteles:**
- Gestión de usuarios del cuartel (solo Jefe Cuartel)
- Asignación de roles operativos

**En Talleres:**
- Gestión de empleados del taller (solo Admin Taller)
- Asignación de mecánicos a órdenes de trabajo

### 4.7. **Catálogos Maestros**

SIGVE mantiene catálogos centralizados configurables que garantizan la estandarización de datos:

- **Tipos de Vehículo**: Carro Bomba, Ambulancia, Escalera, etc.
- **Estados de Vehículo**: Disponible, En Taller, De Baja, etc.
- **Tipos de Combustible**: Gasolina 95, Diesel, Eléctrico, etc.
- **Tipos de Transmisión**: Manual, Automática, CVT, etc.
- **Tipos de Aceite**: 10W-40 Sintético, 5W-30, etc.
- **Tipos de Refrigerante**: Orgánico (Rojo), Inorgánico (Verde), etc.
- **Tipos de Tarea**: Cambio de Aceite, Revisión de Frenos, etc.
- **Roles de Usuario**: Configuración de roles del sistema

Todos los catálogos son gestionables desde el panel SIGVE, permitiendo agregar, editar y eliminar items según las necesidades operativas.

### 4.8. **Gestión de Talleres y Cuarteles**

**Talleres:**
- Registro completo: nombre, dirección, contacto, ubicación geográfica
- Asignación de usuarios (Admin Taller y Mecánicos)
- Visualización en mapas (coordenadas geográficas)

**Cuarteles:**
- Registro completo: nombre, dirección, comuna, contacto, ubicación geográfica
- Asignación de vehículos
- Asignación de usuarios (Jefe Cuartel)
- Visualización en mapas

### 4.9. **Dashboards y Reportes**

**Dashboard SIGVE:**
- Estadísticas globales:
  - Total de talleres y cuarteles
  - Total de vehículos en el sistema
  - Vehículos disponibles vs. en mantenimiento
- Actividad reciente del sistema
- Solicitudes pendientes de aprobación
- Vista de ubicaciones en mapa

**Dashboard Taller:**
- Estadísticas operativas:
  - Órdenes en taller (activas)
  - Órdenes pendientes
  - Órdenes en espera de repuestos
  - Total de órdenes
  - Repuestos con stock bajo
- Lista de órdenes activas
- Accesos rápidos a funcionalidades principales

**Dashboard Cuartel:**
- Estadísticas de la flota:
  - Total de vehículos del cuartel
  - Vehículos disponibles
  - Vehículos en mantenimiento
  - Vehículos de baja
- Distribución de vehículos por tipo
- Lista de vehículos recientes

---

## 5. FLUJOS DE TRABAJO PRINCIPALES

### 5.1. **Flujo de Mantenimiento de Vehículo**

1. **Cuartel identifica necesidad**: El Jefe Cuartel detecta que un vehículo requiere mantenimiento
2. **Creación de solicitud**: Se crea una solicitud de mantenimiento desde el cuartel
3. **Taller recibe solicitud**: El taller visualiza la solicitud pendiente
4. **Creación de orden**: El taller crea una orden de mantenimiento asociada al vehículo
5. **Vehículo ingresa al taller**: El estado del vehículo cambia automáticamente a "En Taller"
6. **Ejecución de mantenimiento**:
   - Se registran las tareas a realizar
   - Se asignan repuestos del inventario a cada tarea
   - El inventario se descuenta automáticamente
7. **Finalización**: Al completar la orden, el vehículo se marca automáticamente como "Disponible"
8. **Registro histórico**: Todo el proceso queda registrado en el historial del vehículo

### 5.2. **Flujo de Solicitud de Datos (Taller → SIGVE)**

1. **Taller identifica necesidad**: El taller necesita un repuesto o dato que no existe en el catálogo
2. **Creación de solicitud**: Se crea una solicitud de datos con el formulario correspondiente
3. **SIGVE revisa**: El administrador SIGVE visualiza la solicitud pendiente
4. **Aprobación/Rechazo**: 
   - Si se aprueba: El sistema crea automáticamente el registro solicitado (repuesto, proveedor, etc.)
   - Si se rechaza: Se registra la razón del rechazo
5. **Notificación**: El taller puede ver el estado de su solicitud

### 5.3. **Flujo de Gestión de Inventario**

1. **SIGVE mantiene catálogo maestro**: Todos los repuestos disponibles están en el catálogo central
2. **Taller solicita repuesto nuevo**: Si un repuesto no existe, se solicita a SIGVE
3. **Taller agrega al inventario**: Una vez aprobado, el taller puede agregarlo a su inventario
4. **Control de stock**: El taller gestiona cantidades, costos y ubicaciones
5. **Uso en órdenes**: Al usar repuestos, se descuentan automáticamente
6. **Alertas**: El sistema alerta cuando el stock está bajo

---

## 6. CARACTERÍSTICAS TÉCNICAS Y DE NEGOCIO

### 6.1. **Trazabilidad Completa**
- Historial completo de cambios de estado de vehículos
- Registro de quién realizó cada acción y cuándo
- Auditoría de todas las operaciones críticas

### 6.2. **Automatización Inteligente**
- Cambio automático de estados de vehículos según el estado de las órdenes
- Descuento automático de inventario al usar repuestos
- Cálculo automático de costos de mantenimiento
- Alertas automáticas de stock bajo

### 6.3. **Estandarización de Datos**
- Catálogos maestros centralizados garantizan consistencia
- Validación de datos en todos los niveles
- Prevención de duplicados y errores

### 6.4. **Escalabilidad**
- Sistema multi-tenant: soporta múltiples talleres y cuarteles
- Gestión centralizada con operación descentralizada
- Fácil incorporación de nuevos talleres y cuarteles

### 6.5. **Integración Geográfica**
- Ubicación de talleres y cuarteles en mapas
- Visualización geográfica de la red de operaciones

### 6.6. **Interfaz Intuitiva**
- Dashboards personalizados por rol
- Accesos rápidos a funcionalidades frecuentes
- Modales y formularios dinámicos para operaciones rápidas
- Búsqueda y filtrado avanzado en todas las listas

---

## 7. VALOR DE NEGOCIO

### 7.1. **Eficiencia Operativa**
- Reducción de tiempos de gestión administrativa
- Automatización de procesos manuales
- Eliminación de errores por duplicación de datos

### 7.2. **Visibilidad y Control**
- Visión centralizada del estado de toda la flota
- Toma de decisiones basada en datos reales
- Identificación proactiva de problemas (stock bajo, vehículos en mantenimiento prolongado)

### 7.3. **Optimización de Recursos**
- Control preciso de inventarios
- Reducción de sobrestock y faltantes
- Optimización de tiempos de mantenimiento

### 7.4. **Cumplimiento y Auditoría**
- Registro completo de todas las operaciones
- Trazabilidad de mantenimientos
- Documentación para cumplimiento normativo

### 7.5. **Coordinación Mejorada**
- Comunicación estructurada entre cuarteles y talleres
- Procesos de solicitud y aprobación claros
- Reducción de malentendidos y retrabajos

---

## 8. CASOS DE USO PRINCIPALES

1. **Un cuartel necesita enviar un vehículo a mantenimiento**: Crea una solicitud, el taller la recibe y genera la orden correspondiente.

2. **Un taller necesita un repuesto que no está en el catálogo**: Solicita la creación del repuesto a SIGVE, quien lo aprueba y lo agrega al catálogo maestro.

3. **Un mecánico está trabajando en una orden**: Registra las tareas realizadas, asigna repuestos del inventario, y el sistema descuenta automáticamente el stock.

4. **Un administrador SIGVE necesita conocer el estado de la flota**: Consulta el dashboard y ve estadísticas globales, vehículos disponibles, en mantenimiento, y solicitudes pendientes.

5. **Un jefe de cuartel necesita saber qué vehículos tiene disponibles**: Consulta su dashboard y ve el estado de todos los vehículos de su cuartel, con filtros por tipo y estado.

6. **Un taller necesita reponer stock de un repuesto**: Consulta su inventario, identifica repuestos con stock bajo, y puede solicitar nuevos repuestos o actualizar cantidades.

---

## 9. CONCLUSIONES

SIGVE es una solución integral que transforma la gestión de vehículos de emergencia de un proceso manual y descentralizado a un sistema digitalizado, centralizado y eficiente. La plataforma no solo gestiona vehículos, sino que coordina toda la cadena de valor: desde la operación en los cuarteles hasta el mantenimiento en los talleres, pasando por la administración central.

La arquitectura modular permite que cada actor (cuartel, taller, administración central) tenga las herramientas específicas que necesita, mientras que la centralización garantiza la consistencia de datos y la visibilidad global necesaria para la toma de decisiones estratégicas.

El sistema está diseñado para crecer y adaptarse a las necesidades cambiantes, con catálogos configurables, roles flexibles y procesos automatizados que reducen la carga administrativa y permiten enfocarse en lo más importante: mantener la flota operativa y lista para responder a emergencias.

