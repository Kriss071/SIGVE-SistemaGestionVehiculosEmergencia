-- Agregar campos de coordenadas geográficas para mapas
-- Este script debe ejecutarse en Supabase SQL Editor

-- Agregar latitud y longitud a la tabla workshop
ALTER TABLE workshop
ADD COLUMN latitude DECIMAL(10, 8),
ADD COLUMN longitude DECIMAL(11, 8);

COMMENT ON COLUMN workshop.latitude IS 'Latitud de la ubicación del taller (ej: -33.4489)';
COMMENT ON COLUMN workshop.longitude IS 'Longitud de la ubicación del taller (ej: -70.6693)';

-- Agregar latitud y longitud a la tabla fire_station
ALTER TABLE fire_station
ADD COLUMN latitude DECIMAL(10, 8),
ADD COLUMN longitude DECIMAL(11, 8);

COMMENT ON COLUMN fire_station.latitude IS 'Latitud de la ubicación del cuartel (ej: -33.4489)';
COMMENT ON COLUMN fire_station.longitude IS 'Longitud de la ubicación del cuartel (ej: -70.6693)';

-- Índices para mejorar el rendimiento de consultas geográficas (opcional)
CREATE INDEX IF NOT EXISTS idx_workshop_coordinates ON workshop(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_fire_station_coordinates ON fire_station(latitude, longitude);

