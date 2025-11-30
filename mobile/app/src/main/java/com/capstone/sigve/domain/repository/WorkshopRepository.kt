package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.Workshop

interface WorkshopRepository {
    /**
     * Obtiene la información del taller por su ID
     */
    suspend fun getWorkshopById(workshopId: Int): Result<Workshop>
    
    /**
     * Obtiene las órdenes de mantención activas de un taller
     * Estados activos: "Pendiente", "En Taller", "En Espera de Repuestos"
     */
    suspend fun getActiveMaintenanceOrders(workshopId: Int): Result<List<MaintenanceOrder>>
}

