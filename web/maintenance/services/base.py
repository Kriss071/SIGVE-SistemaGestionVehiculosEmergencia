from abc import ABC, abstractmethod


class MaintenanceService(ABC):
    
    @abstractmethod
    def list_maintenance(self):
        pass