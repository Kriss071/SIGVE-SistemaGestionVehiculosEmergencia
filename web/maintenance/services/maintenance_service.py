from .base import MaintenanceService
from accounts.client.supabase_client import get_supabase_with_user


class SupabaseMaintenanceService(MaintenanceService):
    def __init__(self, token: str, refresh_token: str):
        self.client = get_supabase_with_user(token, refresh_token)

    def list_maintenance(self):
        try:
            response = self.client.table("mantencion").select("*, vehiculo_id ( patente, estado_mantencion )").execute()
        
            for item in response.data:
                vehicle = item.get('vehiculo_id')
                if isinstance(vehicle, dict):
                    item['vehiculo_patente'] = vehicle.get('patente')
                    item['estado_mantencion'] = vehicle.get('estado_mantencion')
                else: 
                    item['vehiculo_patente'] = 'N/A'
                
            print(response.data)
            return response.data
        except Exception as e:
            print(f"Error al obtener mantenciones: {e}")
            return []
