from datetime import date, datetime
from .base import VehicleService
from accounts.client.supabase_client import get_supabase_with_user


class SupabaseVehicleService(VehicleService):
    def __init__(self, token: str, refresh_token: str):
        self.client = get_supabase_with_user(token, refresh_token)

    def list_vehicles(self):
        response = self.client.table("vehiculo").select("*").execute()
        return response.data

    def add_vehicle(self, data):
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                data[key] = value.isoformat()

        response = self.client.table("vehiculo").insert(data).execute()
        return response.data

    def search_vehicles(self, query: str):
        if not query:
            return self.list_vehicles()

        q = query.lower()

        response = (
            self.client.table("vehiculo")
            .select("*")
            .or_(
                f"patente.ilike.*{q}*,"
                f"marca.ilike.*{q}*,"
                f"modelo.ilike.*{q}*,"
                f"tipo_vehiculo.ilike.*{q}*,"
                f"estado_mantencion.ilike.*{q}*"
            )
            .execute()
        )

        if q.isdigit():
            response.data = [
                v for v in response.data if str(v.get("anio", "")).startswith(q)
            ]

        return response.data

    def get_vehicle(self, patente: str):
        response = (
            self.client.table("vehiculo")
            .select("*")
            .eq("patente", patente)
            .maybe_single()
            .execute()
        )
        return response.data
