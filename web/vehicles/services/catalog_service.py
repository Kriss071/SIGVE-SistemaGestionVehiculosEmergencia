from typing import List, Dict, Any
from accounts.client.supabase_client import get_supabase


class CatalogService:
    """Servicio para obtener datos de tablas de catálogo/lookup"""
    
    @staticmethod
    def get_fire_stations() -> List[Dict[str, Any]]:
        """Obtiene todas las estaciones de bomberos"""
        supabase = get_supabase()
        response = supabase.table("fire_station").select("id, name, address").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_vehicle_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de vehículos"""
        supabase = get_supabase()
        response = supabase.table("vehicle_type").select("id, name, description").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_vehicle_statuses() -> List[Dict[str, Any]]:
        """Obtiene todos los estados de vehículos"""
        supabase = get_supabase()
        response = supabase.table("vehicle_status").select("id, name, description").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_fuel_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de combustible"""
        supabase = get_supabase()
        response = supabase.table("fuel_type").select("id, name").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_transmission_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de transmisión"""
        supabase = get_supabase()
        response = supabase.table("transmission_type").select("id, name").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_oil_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de aceite"""
        supabase = get_supabase()
        response = supabase.table("oil_type").select("id, name, description").order("name").execute()
        return response.data or []
    
    @staticmethod
    def get_coolant_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de refrigerante"""
        supabase = get_supabase()
        response = supabase.table("coolant_type").select("id, name, description").order("name").execute()
        return response.data or []

