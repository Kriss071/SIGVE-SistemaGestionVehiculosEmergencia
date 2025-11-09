import logging
from typing import Dict, Any
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class DashboardService(WorkshopBaseService):
    """Servicio para el dashboard del taller."""
    
    @staticmethod
    def get_statistics(workshop_id: int) -> Dict[str, Any]:
        """
        Obtiene las estadísticas del dashboard para un taller específico.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Diccionario con las estadísticas.
        """
        client = WorkshopBaseService.get_client()
        stats = {}
        
        try:
            # Órdenes en taller
            ordenes_en_taller = client.table("maintenance_order") \
                .select("id", count="exact") \
                .eq("workshop_id", workshop_id) \
                .eq("order_status_id", client.table("maintenance_order_status")
                    .select("id").eq("name", "En Taller").maybe_single().execute().data.get('id', 0)) \
                .execute()
            stats['ordenes_en_taller'] = ordenes_en_taller.count or 0
        except Exception as e:
            logger.error(f"❌ Error contando órdenes en taller: {e}")
            stats['ordenes_en_taller'] = 0
        
        try:
            # Órdenes pendientes
            ordenes_pendientes = client.table("maintenance_order") \
                .select("id", count="exact") \
                .eq("workshop_id", workshop_id) \
                .eq("order_status_id", client.table("maintenance_order_status")
                    .select("id").eq("name", "Pendiente").maybe_single().execute().data.get('id', 0)) \
                .execute()
            stats['ordenes_pendientes'] = ordenes_pendientes.count or 0
        except Exception as e:
            logger.error(f"❌ Error contando órdenes pendientes: {e}")
            stats['ordenes_pendientes'] = 0
        
        try:
            # Órdenes en espera de repuestos
            ordenes_espera_repuesto = client.table("maintenance_order") \
                .select("id", count="exact") \
                .eq("workshop_id", workshop_id) \
                .eq("order_status_id", client.table("maintenance_order_status")
                    .select("id").eq("name", "En Espera de Repuestos").maybe_single().execute().data.get('id', 0)) \
                .execute()
            stats['ordenes_espera_repuesto'] = ordenes_espera_repuesto.count or 0
        except Exception as e:
            logger.error(f"❌ Error contando órdenes en espera de repuestos: {e}")
            stats['ordenes_espera_repuesto'] = 0
        
        try:
            # Total de órdenes
            total_ordenes = client.table("maintenance_order") \
                .select("id", count="exact") \
                .eq("workshop_id", workshop_id) \
                .execute()
            stats['total_ordenes'] = total_ordenes.count or 0
        except Exception as e:
            logger.error(f"❌ Error contando total de órdenes: {e}")
            stats['total_ordenes'] = 0
        
        try:
            # Repuestos con stock bajo (menos de 5 unidades)
            repuestos_bajo_stock = client.table("workshop_inventory") \
                .select("id", count="exact") \
                .eq("workshop_id", workshop_id) \
                .lt("quantity", 5) \
                .execute()
            stats['repuestos_bajo_stock'] = repuestos_bajo_stock.count or 0
        except Exception as e:
            logger.error(f"❌ Error contando repuestos con stock bajo: {e}")
            stats['repuestos_bajo_stock'] = 0
        
        return stats
    
    @staticmethod
    def get_active_orders(workshop_id: int, limit: int = 10):
        """
        Obtiene las órdenes activas (en taller) del taller.
        
        Args:
            workshop_id: ID del taller.
            limit: Número máximo de órdenes a retornar.
            
        Returns:
            Lista de órdenes activas con información del vehículo.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Primero obtener el ID del estado "En Taller"
            status_resp = client.table("maintenance_order_status") \
                .select("id") \
                .eq("name", "En Taller") \
                .maybe_single() \
                .execute()
            
            if not status_resp.data:
                logger.warning("⚠️ No se encontró el estado 'En Taller'")
                return []
            
            status_id = status_resp.data.get('id')
            
            # Obtener las órdenes activas
            query = client.table("maintenance_order") \
                .select("""
                    id,
                    entry_date,
                    mileage,
                    observations,
                    vehicle:vehicle_id(
                        license_plate,
                        brand,
                        model,
                        year,
                        vehicle_status:vehicle_status_id(id, name)
                    ),
                    maintenance_type:maintenance_type_id(name)
                """) \
                .eq("workshop_id", workshop_id) \
                .eq("order_status_id", status_id) \
                .order("entry_date", desc=True) \
                .limit(limit)
            
            return WorkshopBaseService._execute_query(query, "get_active_orders")
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo órdenes activas: {e}", exc_info=True)
            return []


