from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Vehicle:
    # Campos principales
    id: int
    license_plate: str  # patente
    brand: str  # marca
    model: str  # modelo
    year: int  # anio
    
    # Campos adicionales
    engine_number: Optional[str] = None  # numero motor
    vin: Optional[str] = None  # numero chasis
    mileage: Optional[int] = None  # kilometraje
    mileage_last_updated: Optional[date] = None
    oil_capacity_liters: Optional[float] = None
    registration_date: Optional[date] = None
    next_revision_date: Optional[date] = None
    
    # Relaciones (IDs)
    fire_station_id: int = None
    vehicle_type_id: int = None
    vehicle_status_id: int = None
    fuel_type_id: Optional[int] = None
    transmission_type_id: Optional[int] = None
    oil_type_id: Optional[int] = None
    coolant_type_id: Optional[int] = None
    
    # Campos de auditoría
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Campos denormalizados para fácil acceso
    fire_station_name: Optional[str] = None
    vehicle_type_name: Optional[str] = None
    vehicle_status_name: Optional[str] = None
    fuel_type_name: Optional[str] = None
    transmission_type_name: Optional[str] = None
    oil_type_name: Optional[str] = None
    coolant_type_name: Optional[str] = None