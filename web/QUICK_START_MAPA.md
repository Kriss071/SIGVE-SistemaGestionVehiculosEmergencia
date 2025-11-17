# 🚀 Guía Rápida - Sistema de Mapas SIGVE

## ⚡ Inicio Rápido (5 minutos)

### Paso 1: Ejecutar Migración SQL (OBLIGATORIO)

1. Abre **Supabase Dashboard** → SQL Editor
2. Copia y ejecuta el contenido de: `database/migrations/add_location_coordinates.sql`
3. Verifica el resultado (debe mostrar "Success")

```sql
-- Verificar que las columnas se crearon:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'workshop' AND column_name IN ('latitude', 'longitude');
```

### Paso 2: Reiniciar el Servidor Django

```bash
# Si el servidor está corriendo, reinícialo
python manage.py runserver
```

### Paso 3: Probar el Mapa

1. Accede a: `http://localhost:8000/sigve/`
2. Verás el mapa en la parte inferior del dashboard
3. Si no hay marcadores, es normal (aún no hay ubicaciones registradas)

---

## 📍 Agregar tu Primera Ubicación

### Crear un Taller con Ubicación

1. En el Dashboard, haz clic en **"Crear Taller"**
2. Llena el formulario:
   - **Nombre:** `Taller Central`
   - **Dirección:** `Av. Libertador Bernardo O'Higgins 1234, Santiago, Chile`
   - **Teléfono:** (opcional)
   - **Email:** (opcional)
3. Haz clic en **"🔍 Buscar ubicación"** (botón debajo de dirección)
4. Espera 2-3 segundos
5. Verás "✅ Ubicación encontrada"
6. Haz clic en **"Guardar Taller"**
7. La página se recargará y verás el marcador azul en el mapa

### Crear un Cuartel con Ubicación

1. En el Dashboard, haz clic en **"Crear Cuartel"**
2. Llena el formulario:
   - **Nombre:** `Primera Compañía`
   - **Dirección:** `Morandé 360, Santiago, Chile`
   - **Comuna:** Selecciona una comuna
3. Haz clic en **"🔍 Buscar ubicación"**
4. Espera 2-3 segundos
5. Verás "✅ Ubicación encontrada"
6. Haz clic en **"Guardar Cuartel"**
7. La página se recargará y verás el marcador rojo en el mapa

---

## 🎮 Usar el Mapa

### Ver Información de una Ubicación
- Haz clic en cualquier marcador (azul o rojo)
- Se abrirá un popup con la información

### Filtrar Ubicaciones
- Usa los botones en la esquina superior derecha del mapa:
  - **"Talleres"** (azul) - Mostrar/ocultar talleres
  - **"Cuarteles"** (rojo) - Mostrar/ocultar cuarteles

### Navegar el Mapa
- **Zoom:** Rueda del mouse o botones +/-
- **Mover:** Arrastra con el mouse
- **En móvil:** Usa gestos táctiles (pinch to zoom)

---

## ⚠️ Solución Rápida de Problemas

### ❌ "El mapa no aparece"
**Solución:**
1. Verifica que ejecutaste la migración SQL
2. Recarga la página (Ctrl + F5)
3. Revisa la consola del navegador (F12)

### ❌ "Buscar ubicación no funciona"
**Soluciones:**
1. Verifica que la dirección sea específica
2. Incluye comuna, ciudad y "Chile"
3. Ejemplo: `Av. Providencia 1234, Providencia, Santiago, Chile`
4. Intenta con una dirección más conocida

### ❌ "No aparecen marcadores en el mapa"
**Soluciones:**
1. Verifica que los talleres/cuarteles tengan coordenadas
2. Revisa que los filtros estén activados
3. Verifica en la base de datos:
```sql
SELECT name, latitude, longitude FROM workshop;
SELECT name, latitude, longitude FROM fire_station;
```

---

## 💡 Consejos Rápidos

### ✅ Mejores Prácticas para Direcciones

**❌ NO:**
- "Las Hortensias 567"
- "Providencia"

**✅ SÍ:**
- "Calle Las Hortensias 567, Providencia, Santiago, Chile"
- "Av. Libertador Bernardo O'Higgins 1234, Santiago Centro, Santiago, Chile"

### ⚡ Atajos de Teclado en el Mapa
- **+** - Acercar zoom
- **-** - Alejar zoom
- **Flechas** - Mover el mapa
- **Home** - Centrar en todas las ubicaciones

---

## 📚 Documentación Completa

Si necesitas más información:

1. **INSTALACION_MAPA.md** - Guía completa de instalación
2. **ARQUITECTURA_MAPAS.md** - Documentación técnica
3. **RESUMEN_MAPAS.md** - Resumen ejecutivo

---

## ✅ Checklist de Verificación

Marca cada paso al completarlo:

- [ ] Ejecuté la migración SQL en Supabase
- [ ] Verifiqué que las columnas latitude/longitude existen
- [ ] Reinicié el servidor Django
- [ ] Accedí al Dashboard y veo el mapa (aunque esté vacío)
- [ ] Creé un taller con ubicación
- [ ] El marcador aparece en el mapa
- [ ] Puedo hacer clic en el marcador y ver información
- [ ] Los filtros funcionan correctamente

---

**¡Listo! El sistema de mapas está funcionando** 🎉

Si todo está marcado, tienes el sistema de mapas completamente operativo.

---

**SIGVE - Sistema de Gestión de Vehículos de Emergencia**

