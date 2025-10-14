from abc import ABC, abstractmethod
from typing import Any, Dict, List

class VehicleService(ABC):
    @abstractmethod
    def list_vehicles(self):
        pass
    
    @abstractmethod
    def add_vehicle(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def search_vehicles(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_vehicle(self, patente: str) -> Dict[str, Any]:
        pass
    