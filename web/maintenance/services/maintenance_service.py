from .base import MaintenanceService
from accounts.client.supabase_client import get_supabase_with_user


class SupabaseMaintenanceService(MaintenanceService):
    def __init__(self, token: str, refresh_token: str):
        self.client = get_supabase_with_user(token, refresh_token)

    def list_maintenance(self):
        """Lista todas las órdenes de mantenimiento con información relacionada"""
        try:
            response = (
                self.client.table("maintenance_order")
                .select(
                    """
                    *,
                    vehicle:vehicle_id(license_plate, brand, model, vehicle_status:vehicle_status_id(name)),
                    workshop:workshop_id(name, address),
                    employee:employee_id(first_name, last_name)
                    """
                )
                .order("entry_date", desc=True)
                .execute()
            )
            
            # Normalizar datos para compatibilidad
            maintenance_orders = []
            for item in response.data:
                # Extraer info del vehículo
                vehicle = item.get('vehicle', {})
                if isinstance(vehicle, dict):
                    item['vehicle_license_plate'] = vehicle.get('license_plate', 'N/A')
                    item['vehicle_brand'] = vehicle.get('brand', '')
                    item['vehicle_model'] = vehicle.get('model', '')
                    
                    # Estado del vehículo
                    vehicle_status = vehicle.get('vehicle_status')
                    if isinstance(vehicle_status, dict):
                        item['vehicle_status_name'] = vehicle_status.get('name', 'N/A')
                    else:
                        item['vehicle_status_name'] = 'N/A'
                else:
                    item['vehicle_license_plate'] = 'N/A'
                    item['vehicle_brand'] = ''
                    item['vehicle_model'] = ''
                    item['vehicle_status_name'] = 'N/A'
                
                # Info del taller
                workshop = item.get('workshop', {})
                if isinstance(workshop, dict):
                    item['workshop_name'] = workshop.get('name', 'N/A')
                else:
                    item['workshop_name'] = 'N/A'
                
                # Info del empleado
                employee = item.get('employee', {})
                if isinstance(employee, dict):
                    first_name = employee.get('first_name', '')
                    last_name = employee.get('last_name', '')
                    item['employee_name'] = f"{first_name} {last_name}".strip()
                else:
                    item['employee_name'] = 'N/A'
                
                maintenance_orders.append(item)
            
            return maintenance_orders
        except Exception as e:
            print(f"Error al obtener mantenciones: {e}")
            return []
