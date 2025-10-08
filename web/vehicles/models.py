from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Vehicle:
    vehiculo_id: int
    patente: str
    estado_mantencion: str
    kilometraje_actual: float
    tipo_vehiculo: str
    marca: str
    modelo: str
    anio: int
    fecha_ingreso: date
    observaciones: Optional[str] = None