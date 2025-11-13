import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from decimal import Decimal
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class OrderService(WorkshopBaseService):
    """Servicio para gestionar órdenes de mantención."""
    
    # Keywords para identificar estados de finalización
    COMPLETION_KEYWORDS: Set[str] = {'cancel', 'termin', 'final', 'complet', 'cerrad'}
    
    @staticmethod
    def _convert_decimal_to_float(value: Any) -> Any:
        """
        Convierte un valor Decimal a float para serialización JSON.
        
        Args:
            value: Valor que puede ser Decimal, float, int, etc.
            
        Returns:
            float si era Decimal, el valor original en caso contrario.
        """
        if isinstance(value, Decimal):
            return float(value)
        return value
    
    @staticmethod
    def is_completion_status(status_name: str) -> bool:
        """
        Verifica si un nombre de estado indica finalización de orden.
        
        Args:
            status_name: Nombre del estado.
            
        Returns:
            True si el estado indica finalización, False en caso contrario.
        """
        if not status_name:
            return False
        
        status_lower = status_name.lower()
        return any(keyword in status_lower for keyword in OrderService.COMPLETION_KEYWORDS)
    
    @staticmethod
    def is_order_completed(order: Dict[str, Any]) -> bool:
        """
        Verifica si una orden está completada/finalizada.
        
        Una orden se considera completada si:
        - Su estado contiene keywords de finalización (terminada, finalizada, etc.)
        - O tiene fecha de salida definida
        
        Args:
            order: Diccionario con información de la orden.
            
        Returns:
            True si la orden está completada, False en caso contrario.
        """
        if not order:
            return False
        
        # Verificar por nombre de estado
        order_status = order.get('order_status') or {}
        status_name = order_status.get('name', '')
        
        if OrderService.is_completion_status(status_name):
            return True
        
        # Verificar por fecha de salida
        exit_date = order.get('exit_date')
        if exit_date:
            return True
        
        return False
    
    @staticmethod
    def get_all_orders(workshop_id: int, filters: Dict[str, Any] = None):
        """
        Obtiene todas las órdenes de mantención de un taller con filtros opcionales.
        
        Args:
            workshop_id: ID del taller.
            filters: Diccionario con filtros opcionales (status, license_plate, fire_station_id).
            
        Returns:
            Lista de órdenes con información relacionada.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_order") \
            .select("""
                id,
                entry_date,
                exit_date,
                mileage,
                total_cost,
                observations,
                vehicle:vehicle_id(
                    id,
                    license_plate,
                    brand,
                    model,
                    year,
                    fire_station:fire_station_id(id, name),
                    vehicle_status:vehicle_status_id(id, name)
                ),
                order_status:order_status_id(id, name),
                maintenance_type:maintenance_type_id(id, name),
                assigned_mechanic:assigned_mechanic_id(id, first_name, last_name)
            """) \
            .eq("workshop_id", workshop_id) \
            .order("entry_date", desc=True)
        
        # Aplicar filtros si existen
        if filters:
            if filters.get('status_id'):
                query = query.eq("order_status_id", filters['status_id'])
            
            # Para license_plate necesitamos filtrar en Python después
            # porque Supabase no soporta filtrado en relaciones anidadas directamente
        
        orders = WorkshopBaseService._execute_query(query, "get_all_orders")
        
        # Filtrar por patente si se especificó
        if filters and filters.get('license_plate'):
            search_plate = filters['license_plate'].lower()
            orders = [
                order for order in orders 
                if order.get('vehicle', {}).get('license_plate', '').lower().find(search_plate) >= 0
            ]
        
        # Filtrar por cuartel si se especificó
        if filters and filters.get('fire_station_id'):
            fire_station_id = int(filters['fire_station_id'])
            orders = [
                order for order in orders 
                if order.get('vehicle', {}).get('fire_station', {}).get('id') == fire_station_id
            ]
        
        return orders
    
    @staticmethod
    def get_order(order_id: int, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una orden específica verificando que pertenezca al taller.
        
        Args:
            order_id: ID de la orden.
            workshop_id: ID del taller.
            
        Returns:
            Datos de la orden o None.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_order") \
            .select("""
                *,
                vehicle:vehicle_id(*, vehicle_status:vehicle_status_id(id, name)),
                order_status:order_status_id(*),
                maintenance_type:maintenance_type_id(*),
                assigned_mechanic:assigned_mechanic_id(id, first_name, last_name, rut)
            """) \
            .eq("id", order_id) \
            .eq("workshop_id", workshop_id)
        
        return WorkshopBaseService._execute_single(query, "get_order")
    
    @staticmethod
    def create_order(workshop_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea una nueva orden de mantención.
        
        Args:
            workshop_id: ID del taller.
            data: Datos de la orden (vehicle_id, mileage, maintenance_type_id, etc).
            
        Returns:
            Datos de la orden creada o None.
        """
        client = WorkshopBaseService.get_client()
        
        # Verificar si el vehículo ya tiene una orden activa
        if OrderService.has_active_order(data['vehicle_id']):
            logger.warning(f"⚠️ Vehículo {data['vehicle_id']} ya posee una orden activa. No se creará una nueva.")
            return None
        
        # Preparar datos de la orden
        order_data = {
            'workshop_id': workshop_id,
            'vehicle_id': data['vehicle_id'],
            'mileage': data['mileage'],
            'maintenance_type_id': data['maintenance_type_id'],
            'order_status_id': data.get('order_status_id'),
            'assigned_mechanic_id': data.get('assigned_mechanic_id'),
            'entry_date': data.get('entry_date', datetime.now().isoformat()),
            'observations': data.get('observations', '')
        }
        
        try:
            result = client.table("maintenance_order").insert(order_data).execute()
            
            if result.data:
                logger.info(f"✅ Orden de mantención creada: {result.data[0]['id']}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando orden de mantención: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_active_orders_for_vehicles(vehicle_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Retorna un mapa vehicle_id -> orden activa (si existe) para los vehículos proporcionados.
        Una orden se considera activa si su estado no es Cancelado/Terminado/Completado/Finalizado
        y si la fecha de salida aún es nula.
        """
        if not vehicle_ids:
            return {}
        
        client = WorkshopBaseService.get_client()
        
        try:
            query = client.table("maintenance_order") \
                .select("""
                    id,
                    vehicle_id,
                    exit_date,
                    created_at,
                    order_status:order_status_id(name)
                """) \
                .in_("vehicle_id", vehicle_ids) \
                .order("created_at", desc=True)
            
            orders = WorkshopBaseService._execute_query(query, "get_active_orders_for_vehicles")
            active_map: Dict[int, Dict[str, Any]] = {}
            
            for order in orders:
                vehicle_id = order.get('vehicle_id')
                if vehicle_id in active_map:
                    continue
                
                status_name = (order.get('order_status') or {}).get('name', '') or ''
                exit_date = order.get('exit_date')
                
                # Usar el método centralizado para verificar si está completada
                is_completed = OrderService.is_completion_status(status_name) or exit_date is not None
                
                if not is_completed:
                    active_map[vehicle_id] = {
                        'order_id': order.get('id'),
                        'status_name': status_name
                    }
            
            return active_map
        except Exception as e:
            logger.error(f"❌ Error obteniendo órdenes activas para vehículos: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def has_active_order(vehicle_id: int) -> bool:
        """
        Indica si el vehículo tiene alguna orden activa.
        """
        active_map = OrderService.get_active_orders_for_vehicles([vehicle_id])
        return vehicle_id in active_map
    
    @staticmethod
    def update_order(order_id: int, workshop_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza una orden de mantención.
        
        Args:
            order_id: ID de la orden.
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Verificar que la orden no esté completada antes de actualizar
            order = OrderService.get_order(order_id, workshop_id)
            if order and OrderService.is_order_completed(order):
                logger.warning(f"⚠️ Intento de actualizar orden completada {order_id}")
                return False
            
            result = client.table("maintenance_order") \
                .update(data) \
                .eq("id", order_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Orden {order_id} actualizada")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando orden {order_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_order_tasks(order_id: int):
        """
        Obtiene todas las tareas de una orden de mantención.
        
        Args:
            order_id: ID de la orden.
            
        Returns:
            Lista de tareas con información de tipo de tarea.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_task") \
            .select("""
                id,
                description,
                cost,
                created_at,
                task_type:task_type_id(id, name, description)
            """) \
            .eq("maintenance_order_id", order_id) \
            .order("created_at")
        
        return WorkshopBaseService._execute_query(query, "get_order_tasks")
    
    @staticmethod
    def create_task(order_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea una nueva tarea en una orden de mantención.
        
        Args:
            order_id: ID de la orden.
            data: Datos de la tarea (task_type_id, description, cost).
            
        Returns:
            Datos de la tarea creada o None.
        """
        client = WorkshopBaseService.get_client()
        
        # Convertir Decimal a float para evitar problemas de serialización JSON
        cost = data.get('cost', 0)
        cost = OrderService._convert_decimal_to_float(cost)
        
        task_data = {
            'maintenance_order_id': order_id,
            'task_type_id': data['task_type_id'],
            'description': data.get('description', ''),
            'cost': cost
        }
        
        try:
            result = client.table("maintenance_task").insert(task_data).execute()
            
            if result.data:
                logger.info(f"✅ Tarea creada para orden {order_id}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando tarea: {e}", exc_info=True)
            return None
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Elimina una tarea de mantención.
        
        Args:
            task_id: ID de la tarea.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Primero eliminar los repuestos asociados
            client.table("maintenance_task_part") \
                .delete() \
                .eq("maintenance_task_id", task_id) \
                .execute()
            
            # Luego eliminar la tarea
            result = client.table("maintenance_task") \
                .delete() \
                .eq("id", task_id) \
                .execute()
            
            logger.info(f"🗑️ Tarea {task_id} eliminada")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando tarea {task_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_task_parts(task_id: int):
        """
        Obtiene todos los repuestos usados en una tarea.
        
        Args:
            task_id: ID de la tarea.
            
        Returns:
            Lista de repuestos usados.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_task_part") \
            .select("""
                id,
                quantity_used,
                cost_per_unit,
                created_at,
                workshop_inventory:workshop_inventory_id(
                    id,
                    spare_part:spare_part_id(id, name, sku, brand)
                )
            """) \
            .eq("maintenance_task_id", task_id)
        
        return WorkshopBaseService._execute_query(query, "get_task_parts")
    
    @staticmethod
    def add_part_to_task(task_id: int, workshop_inventory_id: int, quantity: int) -> Optional[Dict[str, Any]]:
        """
        Agrega un repuesto a una tarea y descuenta del inventario.
        
        Args:
            task_id: ID de la tarea.
            workshop_inventory_id: ID del inventario del taller.
            quantity: Cantidad a usar.
            
        Returns:
            Datos del repuesto agregado o None si falla.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # 1. Obtener el costo actual del repuesto
            inventory = client.table("workshop_inventory") \
                .select("current_cost, quantity") \
                .eq("id", workshop_inventory_id) \
                .maybe_single() \
                .execute()
            
            if not inventory.data:
                logger.error(f"❌ Inventario {workshop_inventory_id} no encontrado")
                return None
            
            current_cost = inventory.data.get('current_cost', 0)
            # Convertir Decimal a float si es necesario (puede venir de la BD como Decimal)
            current_cost = OrderService._convert_decimal_to_float(current_cost)
            available_quantity = inventory.data.get('quantity', 0)
            
            # Verificar stock disponible
            if available_quantity < quantity:
                logger.error(f"❌ Stock insuficiente: disponible={available_quantity}, requerido={quantity}")
                return None
            
            # 2. Crear el registro de uso de repuesto
            part_data = {
                'maintenance_task_id': task_id,
                'workshop_inventory_id': workshop_inventory_id,
                'quantity_used': quantity,
                'cost_per_unit': current_cost
            }
            
            result = client.table("maintenance_task_part").insert(part_data).execute()
            
            if not result.data:
                return None
            
            # 3. Descontar del inventario
            new_quantity = available_quantity - quantity
            client.table("workshop_inventory") \
                .update({'quantity': new_quantity}) \
                .eq("id", workshop_inventory_id) \
                .execute()
            
            logger.info(f"✅ Repuesto agregado a tarea {task_id} y stock actualizado")
            return result.data[0] if isinstance(result.data, list) else result.data
            
        except Exception as e:
            logger.error(f"❌ Error agregando repuesto a tarea: {e}", exc_info=True)
            return None
    
    @staticmethod
    def delete_part_from_task(part_id: int) -> bool:
        """
        Elimina un repuesto de una tarea y devuelve el stock al inventario.
        
        Args:
            part_id: ID del registro maintenance_task_part.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # 1. Obtener la información del repuesto usado
            part = client.table("maintenance_task_part") \
                .select("workshop_inventory_id, quantity_used") \
                .eq("id", part_id) \
                .maybe_single() \
                .execute()
            
            if not part.data:
                logger.error(f"❌ Repuesto usado {part_id} no encontrado")
                return False
            
            workshop_inventory_id = part.data['workshop_inventory_id']
            quantity_used = part.data['quantity_used']
            
            # 2. Obtener el stock actual
            inventory = client.table("workshop_inventory") \
                .select("quantity") \
                .eq("id", workshop_inventory_id) \
                .maybe_single() \
                .execute()
            
            if not inventory.data:
                return False
            
            current_quantity = inventory.data.get('quantity', 0)
            
            # 3. Eliminar el registro
            client.table("maintenance_task_part") \
                .delete() \
                .eq("id", part_id) \
                .execute()
            
            # 4. Devolver el stock
            new_quantity = current_quantity + quantity_used
            client.table("workshop_inventory") \
                .update({'quantity': new_quantity}) \
                .eq("id", workshop_inventory_id) \
                .execute()
            
            logger.info(f"🗑️ Repuesto eliminado de tarea y stock devuelto")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando repuesto de tarea: {e}", exc_info=True)
            return False


