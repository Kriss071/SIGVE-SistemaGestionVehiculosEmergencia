-- #############################################################################
-- # SCRIPT DE DATOS SEMILLA PARA BASE DE DATOS SIGVE
-- #############################################################################
-- Ejecutar este script en el editor SQL de Supabase.
-- REQUISITO: Crear usuarios en el panel de Authentication ANTES de ejecutar.
-- #############################################################################

BEGIN;

-- ==== 1. Inserción de Catálogos y Datos Geográficos (Tablas sin dependencias) ====

-- Tablas de Localización (Chile)
INSERT INTO region (id, name) VALUES
(1, 'Metropolitana de Santiago'),
(2, 'Valparaíso'),
(3, 'Biobío')
ON CONFLICT (id) DO NOTHING;

INSERT INTO province (id, name, region_id) VALUES
(1, 'Santiago', 1),
(2, 'Valparaíso', 2),
(3, 'Concepción', 3)
ON CONFLICT (id) DO NOTHING;

INSERT INTO commune (id, name, province_id) VALUES
(1, 'Santiago Centro', 1),
(2, 'Puente Alto', 1),
(3, 'Viña del Mar', 2),
(4, 'Valparaíso', 2),
(5, 'Concepción', 3),
(6, 'Talcahuano', 3)
ON CONFLICT (id) DO NOTHING;

-- Tipos de Vehículos
INSERT INTO vehicle_type (id, name, description, created_at) VALUES
(1, 'Carro Bomba', 'Vehículo principal para la extinción de incendios.', NOW()),
(2, 'Camioneta de Rescate', 'Equipada para rescates vehiculares y de personas.', NOW()),
(3, 'Escala Telescópica', 'Para trabajos en altura y rescate en edificios.', NOW()),
(4, 'Ambulancia', 'Unidad de soporte vital básico o avanzado.', NOW())
ON CONFLICT (id) DO NOTHING;

-- Estados de Vehículos
INSERT INTO vehicle_status (id, name, description, created_at) VALUES
(1, 'Operativo', 'Vehículo disponible y en servicio.', NOW()),
(2, 'En Mantención', 'Vehículo en taller para reparaciones o mantención preventiva.', NOW()),
(3, 'Fuera de Servicio', 'Vehículo no disponible por fallas mayores o decisión administrativa.', NOW()),
(4, 'De Baja', 'Vehículo retirado permanentemente del servicio.', NOW())
ON CONFLICT (id) DO NOTHING;

-- Tipos de Combustible, Transmisión, Aceite y Refrigerante
INSERT INTO fuel_type (id, name, created_at) VALUES
(1, 'Diésel', NOW()),
(2, 'Gasolina 95', NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO transmission_type (id, name, created_at) VALUES
(1, 'Manual', NOW()),
(2, 'Automática', NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO oil_type (id, name, description, created_at) VALUES
(1, '15W-40 Mineral', 'Aceite mineral multigrado para motores diésel pesados.', NOW()),
(2, '10W-40 Sintético', 'Aceite sintético para motores de alto rendimiento.', NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO coolant_type (id, name, description, created_at) VALUES
(1, 'Orgánico (Rojo)', 'Larga duración, para sistemas de enfriamiento modernos.', NOW()),
(2, 'Inorgánico (Verde)', 'Tecnología convencional.', NOW())
ON CONFLICT (id) DO NOTHING;

-- Tipos de Tareas de Mantención
INSERT INTO task_type (id, name, description, created_at) VALUES
(1, 'Cambio de Aceite y Filtro', 'Reemplazo de aceite de motor y filtro correspondiente.', NOW()),
(2, 'Revisión Sistema de Frenos', 'Inspección y ajuste de frenos, cambio de pastillas si es necesario.', NOW()),
(3, 'Revisión Sistema Eléctrico', 'Chequeo de luces, sirenas, batería y alternador.', NOW()),
(4, 'Reparación de Bomba de Agua', 'Intervención en la bomba de agua del vehículo.', NOW())
ON CONFLICT (id) DO NOTHING;

-- Proveedores de Repuestos
INSERT INTO supplier (id, name, rut, address, phone, email, created_at) VALUES
(1, 'Repuestos Express S.A.', '76.123.456-7', 'Av. 10 de Julio 543, Santiago', '+56221234567', 'ventas@repuestosexpress.cl', NOW()),
(2, 'Frenos y Partes "El Perno"', '78.987.654-K', 'Calle Blanco 123, Valparaíso', '+56321234567', 'contacto@frenoselperno.cl', NOW())
ON CONFLICT (id) DO NOTHING;

-- Roles de Usuario
INSERT INTO role (id, name, description, created_at) VALUES
(1, 'Administrador', 'Control total del sistema.', NOW()),
(2, 'Mecánico', 'Registra y ejecuta órdenes de mantención.', NOW()),
(3, 'Jefe de Taller', 'Supervisa las operaciones del taller.', NOW())
ON CONFLICT (id) DO NOTHING;

-- ==== 2. Inserción de Entidades de Negocio (Dependen de catálogos) ====

-- Cuarteles de Bomberos
INSERT INTO fire_station (id, name, address, commune_id, created_at) VALUES
(1, '1ª Cía. Bomberos de Santiago "Bomba Santiago"', 'Av. Libertador Bernardo O''Higgins 113, Santiago Centro', 1, NOW()),
(2, '5ª Cía. Bomberos de Viña del Mar "Bomba Viña del Mar"', 'Av. Libertad 567, Viña del Mar', 3, NOW()),
(3, '2ª Cía. Bomberos de Concepción "Bomba 2"', 'Orompello 856, Concepción', 5, NOW())
ON CONFLICT (id) DO NOTHING;

-- Talleres Mecánicos
INSERT INTO workshop (id, name, address, phone, created_at, email) VALUES
(1, 'Taller Central SIGVE', 'Santa Rosa 1234, Santiago Centro', '+56987654321', NOW(), 'taller.central@sigve.com'),
(2, 'Taller Regional Valparaíso', 'Av. Argentina 890, Valparaíso', '+56912345678', NOW(), 'taller.valpo@sigve.com')
ON CONFLICT (id) DO NOTHING;

-- ==== 3. Inserción de Vehículos ====
-- (Dependen de Cuarteles y Catálogos de Vehículos)

INSERT INTO vehicle (id, license_plate, brand, model, year, engine_number, vin, mileage, mileage_last_updated, oil_capacity_liters, registration_date, next_revision_date, fire_station_id, vehicle_type_id, vehicle_status_id, fuel_type_id, transmission_type_id, oil_type_id, coolant_type_id, created_at) VALUES
(1, 'ABCD-12', 'Rosenbauer', 'AT', 2020, 'ENG-987654', 'VIN-ABCDEF123456', 45000, '2025-10-01', 15.5, '2020-03-15', '2026-03-31', 1, 1, 1, 1, 2, 1, 1, NOW()),
(2, 'EFGH-34', 'Iveco Magirus', 'Eurocargo', 2018, 'ENG-123456', 'VIN-GHIJKL789012', 82000, '2025-09-15', 12.0, '2018-07-20', '2026-07-31', 2, 3, 2, 1, 1, 1, 2, NOW()),
(3, 'IJKL-56', 'Ford', 'Ranger', 2022, 'ENG-654321', 'VIN-MNOPQR345678', 25000, '2025-10-10', 8.0, '2022-01-10', '2027-01-31', 1, 2, 1, 1, 2, 2, 1, NOW()),
(4, 'MNOP-78', 'Mercedes-Benz', 'Sprinter', 2021, 'ENG-789012', 'VIN-STUVWX901234', 56000, '2025-08-20', 9.5, '2021-05-25', '2026-05-31', 3, 4, 1, 1, 2, 2, 1, NOW())
ON CONFLICT (id) DO NOTHING;

-- ==== 4. Inserción de Repuestos ====
-- (Dependen de Proveedores)

INSERT INTO spare_part (id, name, sku, brand, description, current_cost, supplier_id, created_at) VALUES
(1, 'Filtro de Aceite Motor H14W01', 'SKU-F001', 'Mann-Filter', 'Filtro de aceite para motores diésel pesados.', 15000, 1, NOW()),
(2, 'Pastillas de Freno Delanteras', 'SKU-P002', 'Brembo', 'Juego de pastillas de freno cerámicas.', 45000, 2, NOW()),
(3, 'Ampolleta H4 12V 55W', 'SKU-A003', 'Osram', 'Ampolleta halógena para foco principal.', 5000, 1, NOW())
ON CONFLICT (id) DO NOTHING;

-- #############################################################################
-- # ATENCIÓN: LA SIGUIENTE SECCIÓN REQUIERE ACCIÓN MANUAL
-- #############################################################################

-- ==== 5. Inserción de Empleados ====
-- (Dependen de auth.users, roles y talleres)
-- 1. Cree los usuarios en Supabase Auth.
-- 2. Copie los UUIDs de los usuarios creados.
-- 3. Reemplace los UUIDs de ejemplo de abajo con los reales.

INSERT INTO employee (id, first_name, last_name, rut, phone, is_active, role_id, workshop_id, created_at) VALUES
('c8c658f0-9479-4024-b034-66ddaeec9d14', 'Juan', 'Pérez', '15.111.222-3', '+56911112222', true, 1, 1, NOW()),  -- REEMPLAZAR UUID (Admin)
('99872e83-eaae-4977-8b0b-b9f80d605083', 'Ana', 'González', '18.333.444-5', '+56933334444', true, 2, 1, NOW()),  -- REEMPLAZAR UUID (Mecánico)
('a993bbd3-13dd-43c0-9c70-b72d4639ab89', 'Carlos', 'Soto', '17.555.666-7', '+56955556666', true, 2, 2, NOW()),   -- REEMPLAZAR UUID (Mecánico)
('eb80d04e-454f-4433-aadc-50e584955a33', 'Carlos', 'Soto', '17.775.666-7', '+56955556666', true, 2, 2, NOW())   -- REEMPLAZAR UUID (Mecánico)
ON CONFLICT (id) DO NOTHING;

-- ==== 6. Inserción de Órdenes de Mantención y Tareas ====
-- (Dependen de Empleados, Talleres y Vehículos)

-- Orden para el vehículo con ID 2 (Iveco Magirus)
INSERT INTO maintenance_order (id, employee_id, workshop_id, vehicle_id, entry_date, exit_date, mileage, total_cost, observations, created_at) VALUES
(1, '99872e83-eaae-4977-8b0b-b9f80d605083', 1, 2, '2025-10-20', null, 82500, null, 'Falla en sistema de frenos, ruido al frenar.', NOW())
ON CONFLICT (id) DO NOTHING;

-- Tareas para la orden de mantención 1
INSERT INTO maintenance_task (id, task_type_id, maintenance_order_id, description, cost, created_at) VALUES
(1, 2, 1, 'Se realiza cambio de pastillas y rectificación de discos delanteros.', 75000, NOW()),
(2, 3, 1, 'Luz de baliza trasera derecha quemada. Se reemplaza ampolleta.', 10000, NOW())
ON CONFLICT (id) DO NOTHING;

-- Repuestos usados en las tareas
INSERT INTO maintenance_task_part (id, maintenance_task_id, spare_part_id, quantity_used, cost_per_unit, created_at) VALUES
(1, 1, 2, 1, 45000, NOW()), -- 1 juego de pastillas en la tarea 1
(2, 2, 3, 1, 5000, NOW())  -- 1 ampolleta en la tarea 2
ON CONFLICT (id) DO NOTHING;

-- ==== 7. Inserción de Stock de Repuestos y Logs ====

-- Stock inicial
INSERT INTO spare_part_stock (id, spare_part_id, workshop_id, last_updated_by_employee_id, quantity, location, updated_at) VALUES
(1, 1, 1, 'c8c658f0-9479-4024-b034-66ddaeec9d14', 50, 'Estante B-2', NOW()),
(2, 2, 1, 'c8c658f0-9479-4024-b034-66ddaeec9d14', 20, 'Estante A-1', NOW()),
(3, 3, 1, 'c8c658f0-9479-4024-b034-66ddaeec9d14', 100, 'Caja C-5', NOW())
ON CONFLICT (id) DO NOTHING;

-- Log de cambio de estado para el vehículo que entró a mantención
INSERT INTO vehicle_status_log (id, vehicle_id, changed_by_employee_id, vehicle_status_id, change_date, reason, created_at) VALUES
(1, 2, '99872e83-eaae-4977-8b0b-b9f80d605083', 2, '2025-10-20 09:00:00', 'Ingreso a taller por mantención orden #1', NOW())
ON CONFLICT (id) DO NOTHING;


COMMIT;