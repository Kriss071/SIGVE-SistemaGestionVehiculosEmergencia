import logging
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class WorkshopService(SigveBaseService):
    """Servicio para gestionar talleres."""
    
    @staticmethod
    def get_all_workshops() -> List[Dict[str, Any]]:
        """
        Obtiene todos los talleres con información adicional.
        
        Returns:
            Lista de talleres.
        """
        client = SigveBaseService.get_client()
        query = client.table("workshop") \
            .select("*") \
            .order("name")
        
        workshops = SigveBaseService._execute_query(query, "get_all_workshops")
        
        # Contar empleados para cada taller
        for workshop in workshops:
            try:
                employees_count = client.table("user_profile") \
                    .select("id", count="exact") \
                    .eq("workshop_id", workshop['id']) \
                    .execute()
                workshop['employees_count'] = employees_count.count or 0
            except Exception as e:
                logger.error(f"❌ Error contando empleados del taller {workshop['id']}: {e}")
                workshop['employees_count'] = 0
        
        return workshops
    
    @staticmethod
    def get_workshop(workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un taller específico por ID.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Datos del taller o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("workshop") \
                .select("*") \
                .eq("id", workshop_id) \
                .maybe_single() \
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo taller {workshop_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_workshop(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo taller.
        
        Args:
            data: Datos del taller (name, address, phone, email).
            
        Returns:
            Datos del taller creado o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("workshop").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Taller creado: {data.get('name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando taller: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_workshop(workshop_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un taller existente.
        
        Args:
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("workshop") \
                .update(data) \
                .eq("id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Taller {workshop_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando taller {workshop_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_workshop(workshop_id: int) -> bool:
        """
        Elimina (desactiva) un taller.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            # En lugar de eliminar, podríamos desactivar usuarios asociados
            # Por ahora, intentamos eliminar directamente
            result = client.table("workshop") \
                .delete() \
                .eq("id", workshop_id) \
                .execute()
            
            logger.info(f"🗑️ Taller {workshop_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando taller {workshop_id}: {e}", exc_info=True)
            return False


