# 🔍 Guía de Debugging - Estados de Vehículos

## ⚠️ PROBLEMA IDENTIFICADO Y CORREGIDO

**Causa:** Los nombres de los estados en el código NO coincidían con los de la base de datos.

- **Código original:** Buscaba `"En Mantención"`
- **Base de datos real:** Tiene `"En Taller"`

**✅ YA CORREGIDO** en `apps/workshop/services/order_service.py`

---

## 📍 Dónde Verificar Errores

### **1. Logs de Django (PRINCIPAL)**

Cuando ejecutas el servidor de desarrollo, todos los logs aparecen en la **consola/terminal**.

#### **Windows PowerShell/CMD:**
```powershell
# En la terminal donde ejecutas el servidor
python manage.py runserver

# Verás los logs en tiempo real
```

#### **Logs que debes buscar al CREAR una orden:**

✅ **Logs exitosos:**
```
✅ Orden de mantención creada: 123
✅ Estado del vehículo 456 actualizado a 'En Taller'
✅ Estado del vehículo 456 actualizado a 3 y registrado en historial
```

⚠️ **Logs de advertencia (problemas no críticos):**
```
⚠️ No se proporcionó user_id, no se actualizará el estado del vehículo
⚠️ No se pudo actualizar el estado del vehículo 456
```

❌ **Logs de error (problemas críticos):**
```
❌ Estado 'En Taller' no encontrado en la base de datos
❌ Error actualizando estado del vehículo 456: [detalles del error]
❌ Error creando orden de mantención: [detalles]
```

---

### **2. Verificar en Base de Datos (Supabase)**

#### **A. Verificar que los estados existen**

Ve a Supabase → SQL Editor y ejecuta:

```sql
-- Verificar estados de vehículos
SELECT id, name FROM vehicle_status ORDER BY name;
```

**Deberías ver:**
| id | name |
|----|------|
| 1 | De Baja |
| 2 | Disponible |
| 3 | En Taller |

Si **NO** ves "En Taller", créalo:
```sql
INSERT INTO vehicle_status (name) VALUES ('En Taller');
```

#### **B. Verificar que se registró el cambio en el historial**

Después de crear una orden, ejecuta:

```sql
-- Reemplaza [ID_VEHICULO] con el ID del vehículo que usaste
SELECT 
  vsl.id,
  vsl.change_date,
  vs.name as nuevo_estado,
  vsl.reason,
  up.email as cambiado_por
FROM vehicle_status_log vsl
JOIN vehicle_status vs ON vsl.vehicle_status_id = vs.id
LEFT JOIN user_profile up ON vsl.changed_by_user_id = up.id
WHERE vsl.vehicle_id = [ID_VEHICULO]
ORDER BY vsl.change_date DESC
LIMIT 5;
```

**Resultado esperado:**
| id | change_date | nuevo_estado | reason | cambiado_por |
|----|-------------|--------------|--------|--------------|
| 123 | 2025-11-16 14:30:00 | En Taller | Automático: Orden de mantención #45 creada | tu_email@example.com |

#### **C. Verificar estado actual del vehículo**

```sql
-- Reemplaza [ID_VEHICULO]
SELECT 
  v.id,
  v.license_plate,
  vs.name as estado_actual
FROM vehicle v
JOIN vehicle_status vs ON v.vehicle_status_id = vs.id
WHERE v.id = [ID_VEHICULO];
```

**Resultado esperado después de crear orden:**
| id | license_plate | estado_actual |
|----|---------------|---------------|
| 456 | ABC-123 | En Taller |

---

### **3. Verificar en el Navegador (Red de DevTools)**

#### **Abrir DevTools:**
- **Chrome/Edge:** Presiona `F12` o `Ctrl + Shift + I`
- **Firefox:** Presiona `F12` o `Ctrl + Shift + K`

#### **Pasos:**
1. Ve a la pestaña **"Network"** (Red)
2. Crea una orden de mantención
3. Busca la petición POST a `/workshop/orders/create/` o `/workshop/orders/api/create/`
4. Haz clic en la petición
5. Ve a la pestaña **"Response"** (Respuesta)

**Respuesta exitosa:**
```json
{
  "success": true,
  "order": {
    "id": 123,
    "vehicle_id": 456,
    ...
  }
}
```

**Respuesta con error:**
```json
{
  "success": false,
  "error": "Descripción del error"
}
```

---

### **4. Verificar user_id en Sesión**

El `user_id` debe estar presente en la sesión para que funcione. Verifica:

#### **En el código (temporal para debugging):**

Agrega esto en `apps/workshop/views.py` en la función `order_create_api()`:

```python
@require_workshop_user
@require_POST
def order_create_api(request):
    """Crea una nueva orden de mantención desde el modal."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    
    # 🔍 LÍNEA DE DEBUG - ELIMINAR DESPUÉS
    print(f"🔍 DEBUG: user_id = {user_id}")
    print(f"🔍 DEBUG: workshop_id = {workshop_id}")
    # FIN DEBUG
    
    form = MaintenanceOrderForm(request.POST)
    # ... resto del código
```

Luego, al crear una orden, busca en la consola:
```
🔍 DEBUG: user_id = abc123-def456-...
🔍 DEBUG: workshop_id = 5
```

Si `user_id` es `None`, el problema está en la autenticación.

---

## 🧪 Test de Funcionamiento

### **Test Rápido (5 minutos):**

1. **Ejecuta el servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Abre la consola y déjala visible** (no minimices la ventana)

3. **En el navegador:**
   - Inicia sesión como usuario de taller
   - Ve a "Órdenes de Mantención"
   - Crea una nueva orden
   - **OBSERVA LA CONSOLA** mientras creas la orden

4. **Lo que debes ver en consola:**
   ```
   🚗 Obteniendo vehículos para cuartel X
   ✅ Orden de mantención creada: 123
   ✅ Estado del vehículo 456 actualizado a 'En Taller'
   ✅ Estado del vehículo 456 actualizado a 3 y registrado en historial
   ```

5. **Si ves errores:**
   - Copia TODO el error (incluye el traceback completo)
   - Busca la línea que dice `ERROR` o `❌`
   - Anótalo para revisarlo

---

## ⚡ Soluciones Rápidas a Problemas Comunes

### **Problema 1: "Estado 'En Taller' no encontrado"**

**Causa:** El estado no existe en la tabla `vehicle_status`

**Solución:**
```sql
-- En Supabase SQL Editor
INSERT INTO vehicle_status (name) VALUES ('En Taller');
INSERT INTO vehicle_status (name) VALUES ('Disponible');
```

---

### **Problema 2: "No se proporcionó user_id"**

**Causa:** La sesión no tiene `sb_user_id` o el decorador no lo está agregando

**Verificación:**
```python
# En views.py, agregar print temporal
user_id = request.session.get('sb_user_id')
print(f"🔍 User ID: {user_id}")
```

**Solución:**
- Cierra sesión y vuelve a iniciar sesión
- Verifica que el decorador `@require_workshop_user` esté presente
- Verifica que Supabase esté funcionando correctamente

---

### **Problema 3: No se ve ningún log**

**Causa:** El nivel de logging está muy alto o no está configurado

**Solución temporal:**

En `config/settings.py`, agrega/modifica:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',  # Cambia a DEBUG para ver más detalles
    },
    'loggers': {
        'apps.workshop': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shared': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

### **Problema 4: El vehículo no cambia de estado pero NO hay errores**

**Causa:** Probablemente Supabase RLS (Row Level Security) está bloqueando la actualización

**Verificación:**
```sql
-- En Supabase, verifica las políticas RLS de la tabla vehicle
SELECT * FROM pg_policies WHERE tablename = 'vehicle';
```

**Solución temporal (solo para desarrollo):**
```sql
-- SOLO PARA TESTING - NO EN PRODUCCIÓN
ALTER TABLE vehicle DISABLE ROW LEVEL SECURITY;
ALTER TABLE vehicle_status_log DISABLE ROW LEVEL SECURITY;
```

---

## 📝 Checklist de Debugging

Marca lo que ya verificaste:

- [ ] El servidor de Django está corriendo sin errores
- [ ] Puedo iniciar sesión correctamente como usuario de taller
- [ ] Los estados "En Taller" y "Disponible" existen en `vehicle_status`
- [ ] Veo logs en la consola cuando creo una orden
- [ ] No veo mensajes de error ❌ en la consola
- [ ] El `user_id` se imprime correctamente (no es None)
- [ ] Revisé en Supabase y el vehículo cambió de estado
- [ ] Revisé `vehicle_status_log` y hay un nuevo registro

---

## 🆘 Si Nada Funciona

### **Pasos para obtener ayuda:**

1. **Captura de logs completos:**
   - Reinicia el servidor
   - Intenta crear una orden
   - Copia TODO el output de la consola (desde que inicia hasta que termina)

2. **Query de diagnóstico completo:**
   ```sql
   -- Ejecuta esto y guarda el resultado
   SELECT 
     'Estados de Vehículo' as tipo,
     id::text,
     name,
     NULL as reason
   FROM vehicle_status
   
   UNION ALL
   
   SELECT 
     'Historial Reciente' as tipo,
     vsl.id::text,
     vs.name,
     vsl.reason
   FROM vehicle_status_log vsl
   JOIN vehicle_status vs ON vsl.vehicle_status_id = vs.id
   ORDER BY tipo, id DESC
   LIMIT 20;
   ```

3. **Información del navegador:**
   - Abre DevTools (F12)
   - Ve a Console
   - Copia cualquier error que veas en rojo

4. **Comparte:**
   - Los logs de Django
   - El resultado del query SQL
   - Los errores del navegador (si hay)

---

## 🎯 Resumen de Archivos Clave

| Archivo | Qué hace | Dónde buscar errores |
|---------|----------|---------------------|
| `shared/services/vehicle_status_service.py` | Actualiza estados de vehículos | Línea 66-120 |
| `apps/workshop/services/order_service.py` | Crea/actualiza órdenes | Línea 174-235 (crear), 294-364 (actualizar) |
| `apps/workshop/views.py` | Recibe peticiones del usuario | Línea 169-210 (crear orden) |

---

## 📞 Líneas de Código Exactas para Revisar

Si quieres revisar el código manualmente, busca estas líneas:

### **1. Donde se actualiza el estado al crear orden:**
`apps/workshop/services/order_service.py` - Línea **213-227**

### **2. Donde se actualiza el estado al finalizar orden:**
`apps/workshop/services/order_service.py` - Línea **346-355**

### **3. Donde se obtiene el user_id:**
`apps/workshop/views.py` - Línea **172**

---

**Fecha:** 16 de Noviembre de 2025  
**Versión:** 1.1 (corregido para "En Taller")

