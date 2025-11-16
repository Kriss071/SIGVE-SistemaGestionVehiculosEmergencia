# Guía de Pruebas - Estados de Vehículos y Mantenciones

## 📋 Preparación del Ambiente de Pruebas

### 1. Verificar Estados en Base de Datos

Ejecuta estos queries en Supabase para verificar que existen los estados necesarios:

```sql
-- Verificar estados de vehículos
SELECT id, name FROM vehicle_status ORDER BY name;

-- Deberías ver al menos:
-- - De Baja
-- - Disponible
-- - En Taller

-- Verificar estados de órdenes
SELECT id, name FROM maintenance_order_status ORDER BY name;

-- Deberías ver al menos:
-- - Pendiente
-- - En Taller
-- - En Espera de Repuestos
-- - Terminada
-- - Completada
-- - Cancelada
```

Si faltan estados, créalos:

```sql
-- Crear estados de vehículo faltantes
INSERT INTO vehicle_status (name) 
VALUES ('En Taller') 
ON CONFLICT (name) DO NOTHING;

INSERT INTO vehicle_status (name) 
VALUES ('Disponible') 
ON CONFLICT (name) DO NOTHING;

INSERT INTO vehicle_status (name) 
VALUES ('De Baja') 
ON CONFLICT (name) DO NOTHING;
```

---

## 🧪 Casos de Prueba

### **PRUEBA 1: Crear Orden de Mantención (Modal)**

**Objetivo:** Verificar que al crear una orden, el vehículo cambia a "En Mantención"

**Pasos:**
1. Inicia sesión como usuario de taller (Admin Taller o Mecánico)
2. Ve a "Órdenes de Mantención" en el menú
3. Haz clic en "Nueva Orden" (modal)
4. Busca un vehículo por patente
5. Si el vehículo está "Disponible", continúa
6. Completa el formulario:
   - Kilometraje: 45000
   - Tipo de Mantención: Preventiva
   - Estado de Orden: En Taller
   - Mecánico: (Selecciona uno)
   - Observaciones: "Mantención programada"
7. Haz clic en "Crear Orden"

**Resultado Esperado:**
- ✅ Mensaje: "Orden de mantención #XXX creada correctamente"
- ✅ El vehículo ahora tiene estado "En Taller"
- ✅ En el historial del vehículo aparece un nuevo registro:
  - Estado: En Taller
  - Cambiado por: Tu usuario
  - Razón: "Automático: Orden de mantención #XXX creada"

**Verificación en BD:**
```sql
-- Verificar estado del vehículo
SELECT license_plate, vs.name as estado
FROM vehicle v
JOIN vehicle_status vs ON v.vehicle_status_id = vs.id
WHERE v.id = [ID_DEL_VEHICULO];

-- Debería mostrar: "En Taller"

-- Verificar registro en historial
SELECT 
  vsl.change_date,
  vs.name as nuevo_estado,
  vsl.reason,
  up.email as cambiado_por
FROM vehicle_status_log vsl
JOIN vehicle_status vs ON vsl.vehicle_status_id = vs.id
JOIN user_profile up ON vsl.changed_by_user_id = up.id
WHERE vsl.vehicle_id = [ID_DEL_VEHICULO]
ORDER BY vsl.change_date DESC
LIMIT 1;

-- Debería mostrar el último cambio con razón "Automático: Orden..."
```

---

### **PRUEBA 2: Cambiar Estado de Orden (No Finalizada)**

**Objetivo:** Verificar que cambiar estado de orden (sin finalizar) no afecta el vehículo

**Pasos:**
1. Abre la orden creada en PRUEBA 1
2. En "Información General", cambia:
   - Estado de Orden: "En Espera de Repuestos"
3. Haz clic en "Guardar Cambios"

**Resultado Esperado:**
- ✅ Mensaje: "Orden actualizada correctamente"
- ✅ El vehículo PERMANECE "En Taller"
- ✅ NO hay nuevo registro en vehicle_status_log (el vehículo no cambió de estado)

**Verificación en BD:**
```sql
-- Verificar que el vehículo sigue "En Taller"
SELECT license_plate, vs.name as estado
FROM vehicle v
JOIN vehicle_status vs ON v.vehicle_status_id = vs.id
WHERE v.id = [ID_DEL_VEHICULO];

-- Debería seguir mostrando: "En Taller"
```

---

### **PRUEBA 3: Finalizar Orden de Mantención**

**Objetivo:** Verificar que al finalizar orden, el vehículo vuelve a "Disponible"

**Pasos:**
1. Abre la orden desde PRUEBA 1/2
2. Agrega al menos una tarea (obligatorio para buenas prácticas):
   - Tipo de Tarea: "Cambio de Aceite"
   - Descripción: "Cambio de aceite y filtro"
   - Costo: 25000
3. En "Información General", cambia:
   - Estado de Orden: "Terminada"
4. Aparecerá un modal de confirmación
5. Confirma "Sí, Marcar como Terminada"

**Resultado Esperado:**
- ✅ Mensaje: "Orden marcada como terminada. El vehículo ha sido marcado como Disponible."
- ✅ Todos los campos de la orden quedan deshabilitados (solo lectura)
- ✅ El vehículo ahora tiene estado "Disponible"
- ✅ En el historial del vehículo aparece un nuevo registro:
  - Estado: Disponible
  - Cambiado por: Tu usuario
  - Razón: "Automático: Orden de mantención #XXX finalizada"

**Verificación en BD:**
```sql
-- Verificar estado del vehículo
SELECT license_plate, vs.name as estado
FROM vehicle v
JOIN vehicle_status vs ON v.vehicle_status_id = vs.id
WHERE v.id = [ID_DEL_VEHICULO];

-- Debería mostrar: "Disponible"

-- Verificar registro en historial
SELECT 
  vsl.change_date,
  vs.name as nuevo_estado,
  vsl.reason,
  up.email as cambiado_por
FROM vehicle_status_log vsl
JOIN vehicle_status vs ON vsl.vehicle_status_id = vs.id
JOIN user_profile up ON vsl.changed_by_user_id = up.id
WHERE vsl.vehicle_id = [ID_DEL_VEHICULO]
ORDER BY vsl.change_date DESC
LIMIT 2;

-- Debería mostrar dos registros:
-- 1. "Disponible" con razón "Automático: Orden... finalizada"
-- 2. "En Taller" con razón "Automático: Orden... creada"
```

---

### **PRUEBA 4: Ver Historial desde Fire Station**

**Objetivo:** Verificar que el historial de vehículo se ve correctamente

**Pasos:**
1. Cierra sesión del taller
2. Inicia sesión como usuario de cuartel (Jefe de Cuartel)
3. Ve a "Vehículos"
4. Busca el vehículo usado en las pruebas anteriores
5. Haz clic en el botón "Historial" (ícono de reloj)

**Resultado Esperado:**
- ✅ Se muestra una tabla con el historial de cambios
- ✅ Aparecen los dos cambios recientes:
  - Cambio 1 (más reciente): "Disponible" - "Automático: Orden... finalizada"
  - Cambio 2: "En Taller" - "Automático: Orden... creada"
- ✅ Se muestra el nombre y email del usuario que realizó los cambios
- ✅ Las fechas están correctamente formateadas

---

### **PRUEBA 5: Crear Segunda Orden (Vehículo ya en Mantención)**

**Objetivo:** Verificar que no se puede crear una segunda orden activa

**Pasos:**
1. Crea una nueva orden para un vehículo "Disponible"
2. Verifica que el vehículo cambió a "En Taller"
3. Sin finalizar la primera orden, intenta crear una segunda orden para el mismo vehículo

**Resultado Esperado:**
- ❌ Mensaje de error: "El vehículo seleccionado ya cuenta con una orden activa en el taller."
- ✅ No se crea la segunda orden
- ✅ El vehículo permanece "En Taller"

---

### **PRUEBA 6: Estados de Orden con Keywords de Finalización**

**Objetivo:** Verificar que diferentes palabras clave funcionan

**Pasos:**
1. Crea una orden de mantención (vehículo pasa a "En Mantención")
2. Cambia el estado de la orden a: "Completada" (si existe)
   - Alternativamente: "Cancelada", "Finalizada", "Cerrada"

**Resultado Esperado:**
- ✅ El vehículo vuelve a "Disponible"
- ✅ Se registra en el historial con la razón correspondiente

**Keywords que deben funcionar:**
- Terminada
- Finalizada
- Completada
- Cancelada
- Cerrada
- (Cualquier variación con estas palabras: "Orden Terminada", "Mantención Finalizada", etc.)

---

## 🔍 Verificación de Logs

Para depurar problemas, revisa los logs de Django:

```bash
# En desarrollo (manage.py runserver), busca en la consola:

# Al crear orden:
"✅ Orden de mantención creada: 123"
"✅ Estado del vehículo 456 actualizado a 'En Mantención'"
"✅ Estado del vehículo 456 actualizado a 3 y registrado en historial"

# Al finalizar orden:
"✅ Orden 123 actualizada"
"✅ Vehículo 456 marcado como 'Disponible' al finalizar orden"
"✅ Estado del vehículo 456 actualizado a 1 y registrado en historial"

# Si hay errores:
"❌ Error actualizando estado del vehículo 456: [detalles]"
"⚠️ No se proporcionó user_id, no se actualizará el estado del vehículo"
"❌ Estado 'En Mantención' no encontrado en la base de datos"
```

---

## ⚠️ Problemas Comunes y Soluciones

### Problema: "Estado 'En Taller' no encontrado"

**Causa:** El estado no existe en la tabla `vehicle_status`

**Solución:**
```sql
INSERT INTO vehicle_status (name) VALUES ('En Taller');
INSERT INTO vehicle_status (name) VALUES ('Disponible');
INSERT INTO vehicle_status (name) VALUES ('De Baja');
```

---

### Problema: El vehículo no cambia de estado

**Causa 1:** No se está pasando `user_id` al servicio

**Verificación:**
- Busca en logs: "⚠️ No se proporcionó user_id"
- Verifica que estás autenticado correctamente
- Verifica que `request.session.get('sb_user_id')` devuelve un valor

**Causa 2:** El nombre del estado tiene mayúsculas/minúsculas incorrectas

**Verificación:**
```sql
-- Ver cómo está escrito el estado en BD
SELECT id, name FROM vehicle_status;

-- El servicio usa .ilike() que es case-insensitive, pero asegúrate que exista
```

---

### Problema: Se registra en historial pero el vehículo no cambia

**Causa:** Error en la actualización de la tabla `vehicle`

**Verificación:**
- Busca en logs errores de Supabase
- Verifica permisos RLS en Supabase para la tabla `vehicle`

---

## 📊 Consultas SQL Útiles

### Ver todas las órdenes activas de un vehículo

```sql
SELECT 
  mo.id,
  mo.entry_date,
  mo.exit_date,
  mos.name as estado_orden,
  v.license_plate
FROM maintenance_order mo
JOIN maintenance_order_status mos ON mo.order_status_id = mos.id
JOIN vehicle v ON mo.vehicle_id = v.id
WHERE v.id = [ID_VEHICULO]
  AND mo.exit_date IS NULL
  AND mos.name NOT ILIKE '%termin%'
  AND mos.name NOT ILIKE '%complet%'
  AND mos.name NOT ILIKE '%cancel%'
ORDER BY mo.entry_date DESC;
```

### Ver historial completo de un vehículo

```sql
SELECT 
  v.license_plate,
  vsl.change_date,
  vs.name as estado,
  vsl.reason,
  up.first_name || ' ' || up.last_name as cambiado_por,
  up.email
FROM vehicle_status_log vsl
JOIN vehicle v ON vsl.vehicle_id = v.id
JOIN vehicle_status vs ON vsl.vehicle_status_id = vs.id
LEFT JOIN user_profile up ON vsl.changed_by_user_id = up.id
WHERE v.id = [ID_VEHICULO]
ORDER BY vsl.change_date DESC;
```

### Ver vehículos actualmente en mantención

```sql
SELECT 
  v.license_plate,
  v.brand,
  v.model,
  vs.name as estado,
  fs.name as cuartel,
  mo.id as orden_activa,
  mos.name as estado_orden
FROM vehicle v
JOIN vehicle_status vs ON v.vehicle_status_id = vs.id
JOIN fire_station fs ON v.fire_station_id = fs.id
LEFT JOIN maintenance_order mo ON v.id = mo.vehicle_id 
  AND mo.exit_date IS NULL
LEFT JOIN maintenance_order_status mos ON mo.order_status_id = mos.id
WHERE vs.name = 'En Taller'
ORDER BY v.license_plate;
```

---

## ✅ Checklist de Pruebas Completadas

- [ ] PRUEBA 1: Crear orden (vehículo pasa a "En Taller")
- [ ] PRUEBA 2: Cambiar estado de orden (vehículo permanece igual)
- [ ] PRUEBA 3: Finalizar orden (vehículo vuelve a "Disponible")
- [ ] PRUEBA 4: Ver historial desde Fire Station
- [ ] PRUEBA 5: Intentar crear segunda orden (debe fallar)
- [ ] PRUEBA 6: Keywords de finalización funcionan

- [ ] Verificado en BD: Estados existen
- [ ] Verificado en BD: Registros en vehicle_status_log
- [ ] Verificado en Logs: Sin errores
- [ ] Verificado en UI: Mensajes correctos

---

**Fecha de Documento:** 16 de Noviembre de 2025  
**Versión:** 1.0

