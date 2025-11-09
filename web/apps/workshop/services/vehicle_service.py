import logging
from typing import Dict, List, Any, Optional
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class VehicleService(WorkshopBaseService):
    """Servicio para gestionar vehículos desde la perspectiva del taller."""
    
    @staticmethod
    def search_vehicle(license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Busca un vehículo por patente.
        
        Args:
            license_plate: Patente del vehículo.
            
        Returns:
            Datos del vehículo o None si no existe.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("vehicle") \
            .select("""
                id,
                license_plate,
                brand,
                model,
                year,
                engine_number,
                vin,
                mileage,
                fire_station:fire_station_id(id, name),
                vehicle_type:vehicle_type_id(id, name),
                vehicle_status:vehicle_status_id(id, name),
                fuel_type:fuel_type_id(id, name),
                transmission_type:transmission_type_id(id, name),
                oil_type:oil_type_id(id, name),
                coolant_type:coolant_type_id(id, name)
            """) \
            .eq("license_plate", license_plate.upper())
        
        return WorkshopBaseService._execute_single(query, "search_vehicle")
    
    @staticmethod
    def search_vehicles(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca vehículos por coincidencia parcial de patente.
        
        Args:
            query: Texto a buscar dentro de la patente.
            limit: Máximo de resultados.
            
        Returns:
            Lista de vehículos que coinciden con la búsqueda.
        """
        if not query:
            return []
        
        client = WorkshopBaseService.get_client()
        query = query.upper()
        
        try:
            result = client.table("vehicle") \
                .select("""
                    id,
                    license_plate,
                    brand,
                    model,
                    year,
                    vehicle_status:vehicle_status_id(id, name)
                """) \
                .ilike("license_plate", f"%{query}%") \
                .order("license_plate") \
                .limit(limit) \
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"❌ Error buscando vehículos por patente: {e}", exc_info=True)
            return []
    
    @staticmethod
    def create_vehicle(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo vehículo en el sistema.
        
        Args:
            data: Datos del vehículo.
            
        Returns:
            Datos del vehículo creado o None.
        """
        client = WorkshopBaseService.get_client()
        
        # Asegurar que la patente esté en mayúsculas
        if 'license_plate' in data:
            data['license_plate'] = data['license_plate'].upper()
        
        try:
            # Obtener el estado por defecto "Disponible"
            status = client.table("vehicle_status") \
                .select("id") \
                .eq("name", "Disponible") \
                .maybe_single() \
                .execute()
            
            if status.data:
                data['vehicle_status_id'] = status.data['id']
            
            result = client.table("vehicle").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Vehículo creado: {data['license_plate']}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando vehículo: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_all_fire_stations():
        """
        Obtiene todos los cuarteles para el selector de vehículos.
        
        Returns:
            Lista de cuarteles.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("fire_station") \
            .select("id, name, address") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_all_fire_stations")
    
    @staticmethod
    def get_catalog_data():
        """
        Obtiene todos los datos de catálogo necesarios para crear un vehículo.
        
        Returns:
            Diccionario con listas de tipos de vehículo, combustible, transmisión, etc.
        """
        client = WorkshopBaseService.get_client()
        
        catalog_data = {}
        
        try:
            # Tipos de vehículo
            catalog_data['vehicle_types'] = client.table("vehicle_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de combustible
            catalog_data['fuel_types'] = client.table("fuel_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de transmisión
            catalog_data['transmission_types'] = client.table("transmission_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de aceite
            catalog_data['oil_types'] = client.table("oil_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de refrigerante
            catalog_data['coolant_types'] = client.table("coolant_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de catálogo: {e}", exc_info=True)
        
        return catalog_data
    
    @staticmethod
    def get_maintenance_types():
        """
        Obtiene los tipos de mantención disponibles.
        
        Returns:
            Lista de tipos de mantención.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_type") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_maintenance_types")
    
    @staticmethod
    def get_order_statuses():
        """
        Obtiene los estados de orden disponibles.
        
        Returns:
            Lista de estados de orden.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_order_status") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_order_statuses")
    
    @staticmethod
    def get_task_types():
        """
        Obtiene los tipos de tarea disponibles.
        
        Returns:
            Lista de tipos de tarea.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("task_type") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_task_types")



