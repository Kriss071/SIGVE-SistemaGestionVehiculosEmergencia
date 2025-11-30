package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.MaintenanceOrderDetail
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceTask
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.Mechanic
import com.capstone.sigve.domain.model.TaskType
import com.capstone.sigve.domain.model.Workshop
import com.capstone.sigve.domain.model.WorkshopInventoryItem

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
    
    /**
     * Obtiene TODAS las órdenes de mantención de un taller (incluidas completadas)
     */
    suspend fun getAllMaintenanceOrders(workshopId: Int): Result<List<MaintenanceOrder>>
    
    /**
     * Obtiene el detalle completo de una orden de mantención
     */
    suspend fun getMaintenanceOrderById(orderId: Int): Result<MaintenanceOrderDetail>
    
    /**
     * Obtiene todos los estados de orden de mantención
     */
    suspend fun getMaintenanceOrderStatuses(): Result<List<MaintenanceOrderStatus>>
    
    /**
     * Obtiene todos los tipos de mantención
     */
    suspend fun getMaintenanceTypes(): Result<List<MaintenanceType>>
    
    /**
     * Obtiene los mecánicos de un taller específico
     */
    suspend fun getWorkshopMechanics(workshopId: Int): Result<List<Mechanic>>
    
    /**
     * Obtiene todos los tipos de tareas
     */
    suspend fun getTaskTypes(): Result<List<TaskType>>
    
    /**
     * Obtiene el inventario de un taller
     */
    suspend fun getWorkshopInventory(workshopId: Int): Result<List<WorkshopInventoryItem>>
    
    /**
     * Actualiza una orden de mantención
     */
    suspend fun updateMaintenanceOrder(
        orderId: Int,
        statusId: Int,
        maintenanceTypeId: Int,
        assignedMechanicId: String?,
        exitDate: String?,
        observations: String?,
        totalCost: Double?
    ): Result<Unit>
    
    /**
     * Crea una nueva tarea de mantención
     */
    suspend fun createMaintenanceTask(
        maintenanceOrderId: Int,
        taskTypeId: Int,
        description: String?,
        cost: Double
    ): Result<MaintenanceTask>
    
    /**
     * Agrega un repuesto a una tarea de mantención
     */
    suspend fun addPartToTask(
        maintenanceTaskId: Int,
        workshopInventoryId: Int,
        quantityUsed: Int,
        costPerUnit: Double?
    ): Result<Unit>
    
    /**
     * Elimina una tarea de mantención
     */
    suspend fun deleteMaintenanceTask(taskId: Int): Result<Unit>
    
    /**
     * Elimina un repuesto de una tarea
     */
    suspend fun removePartFromTask(partId: Int): Result<Unit>
}
