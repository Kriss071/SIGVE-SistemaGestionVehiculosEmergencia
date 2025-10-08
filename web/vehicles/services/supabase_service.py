from datetime import date, datetime
from .base import VehicleService
from accounts.supabase_client import get_supabase_with_user

class SupabaseVehicleService(VehicleService):
    def __init__(self, token: str, refresh_token):
        self.client = get_supabase_with_user(token, refresh_token)
        
    def list_vehicles(self):
        response = self.client.table("vehiculo").select("*").execute()
        print(response)
        return response.data
    
    def add_vehicle(self, data):
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                data[key] = value.isoformat()
        
        response = self.client.table("vehiculo").insert(data).execute()
        return response.data