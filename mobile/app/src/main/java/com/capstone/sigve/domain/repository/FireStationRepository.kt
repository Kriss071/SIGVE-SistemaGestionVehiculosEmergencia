package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.FireStation
import com.capstone.sigve.domain.model.FireStationDashboardStats
import com.capstone.sigve.domain.model.FireStationVehicle

interface FireStationRepository {
    /**
     * Obtiene la información del cuartel por su ID
     */
    suspend fun getFireStationById(fireStationId: Int): Result<FireStation>
    
    /**
     * Obtiene todos los vehículos de un cuartel con información de estado y tipo
     */
    suspend fun getFireStationVehicles(fireStationId: Int): Result<List<FireStationVehicle>>
    
    /**
     * Obtiene las estadísticas del dashboard del cuartel
     */
    suspend fun getFireStationStats(fireStationId: Int): Result<FireStationDashboardStats>
    
    /**
     * Obtiene los IDs de vehículos que tienen órdenes de mantención activas
     */
    suspend fun getVehiclesWithActiveMaintenanceOrders(fireStationId: Int): Result<Map<Int, String?>>
}



