from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class VehicleService(ABC):
    """
    Clase Base Abstracta (ABC) para el Servicio de Vehículos.

    Define la interfaz (contrato) que deben seguir todas las implementaciones
    concretas de un servicio de vehículos (ej. SupabaseVehicleService, etc.).
    Esto asegura que cualquier implementación del servicio tendrá los mismos
    métodos públicos con las mismas firmas, promoviendo la consistencia y
    facilitando la sustitución de implementaciones (polimorfismo).
    """

    @abstractmethod
    def list_vehicles(self) -> List[Dict[str, Any]]:
        """
        Método abstracto para listar todos los vehículos.

        Las implementaciones concretas deben devolver una lista de diccionarios,
        donde cada diccionario representa un vehículo.
        """
        pass
    
    @abstractmethod
    def add_vehicle(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Método abstracto para agregar un nuevo vehículo.

        Args:
            data: Un diccionario conteniendo los datos del vehículo a agregar.

        Returns:
             Una lista que contiene el diccionario del vehículo recién creado
             (o los vehículos creados, si la implementación permite múltiples).
             Puede devolver una lista vacía o lanzar una excepción en caso de error.
        """
        pass
    
    @abstractmethod
    def search_vehicles(self, query: str) -> List[Dict[str, Any]]:
        """
        Método abstracto para buscar vehículos según un criterio.

        Args:
            query: El término o criterio de búsqueda (string).

        Returns:
            Una lista de diccionarios con los vehículos que coinciden con la búsqueda.
            Devuelve una lista vacía si no hay coincidencias.
        """
        pass

    @abstractmethod
    def get_vehicle(self, license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Método abstracto para obtener los detalles de un vehículo específico por su patente.

        Args:
            license_plate: La patente (matrícula) del vehículo a buscar.

        Returns:
            Un diccionario con los datos del vehículo si se encuentra,
            o None si no se encuentra ningún vehículo con esa patente.
        """
        pass
    
    @abstractmethod
    def delete_vehicle(self, license_plate: str) -> bool:
        """
        Método abstracto para eliminar un vehículo por su patente.

        Args:
            license_plate: La patente (matrícula) del vehículo a eliminar.

        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        pass
    
    @abstractmethod
    def update_vehicle(self, license_plate: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Método abstracto para actualizar un vehículo existente.

        Args:
            license_plate: La patente (matrícula) del vehículo a actualizar.
            data: Un diccionario con los datos actualizados del vehículo.

        Returns:
            Un diccionario con los datos del vehículo actualizado si fue exitoso,
            o None si no se pudo actualizar.
        """
        pass
    