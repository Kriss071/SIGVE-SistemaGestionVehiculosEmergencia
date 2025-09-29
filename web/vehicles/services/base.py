from abc import ABC, abstractmethod

class VehicleService(ABC):
    @abstractmethod
    def list_vehicles(self):
        pass
    