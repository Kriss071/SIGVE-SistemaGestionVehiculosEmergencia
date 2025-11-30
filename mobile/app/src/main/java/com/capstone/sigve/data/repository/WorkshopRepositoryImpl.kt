package com.capstone.sigve.data.repository

import android.util.Log
import com.capstone.sigve.data.dto.CreateMaintenanceTaskDto
import com.capstone.sigve.data.dto.CreateMaintenanceTaskPartDto
import com.capstone.sigve.data.dto.MaintenanceOrderDetailDto
import com.capstone.sigve.data.dto.MaintenanceOrderDto
import com.capstone.sigve.data.dto.MaintenanceOrderStatusDto
import com.capstone.sigve.data.dto.MaintenanceTaskDto
import com.capstone.sigve.data.dto.MaintenanceTypeDto
import com.capstone.sigve.data.dto.MechanicDto
import com.capstone.sigve.data.dto.TaskTypeDto
import com.capstone.sigve.data.dto.UpdateMaintenanceOrderDto
import com.capstone.sigve.data.dto.WorkshopDto
import com.capstone.sigve.data.dto.WorkshopInventoryDto
import com.capstone.sigve.data.mapper.toDomain
import com.capstone.sigve.data.mapper.toDomainList
import com.capstone.sigve.data.mapper.toDomainTaskList
import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.MaintenanceOrderDetail
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceTask
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.Mechanic
import com.capstone.sigve.domain.model.TaskType
import com.capstone.sigve.domain.model.Workshop
import com.capstone.sigve.domain.model.WorkshopInventoryItem
import com.capstone.sigve.domain.repository.WorkshopRepository
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.postgrest.postgrest
import io.github.jan.supabase.postgrest.query.Columns
import javax.inject.Inject

class WorkshopRepositoryImpl @Inject constructor(
    private val client: SupabaseClient
) : WorkshopRepository {

    companion object {
        private const val TAG = "WorkshopRepository"
    }

    override suspend fun getWorkshopById(workshopId: Int): Result<Workshop> {
        return try {
            Log.d(TAG, "Obteniendo taller con ID: $workshopId")
            
            val workshopDto = client.postgrest["workshop"]
                .select {
                    filter {
                        eq("id", workshopId)
                    }
                }
                .decodeSingle<WorkshopDto>()

            Log.d(TAG, "Taller obtenido: ${workshopDto.name}")
            Result.success(workshopDto.toDomain())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener taller: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getActiveMaintenanceOrders(workshopId: Int): Result<List<MaintenanceOrder>> {
        return try {
            Log.d(TAG, "Obteniendo órdenes activas para taller ID: $workshopId")
            
            val selectColumns = """
                id,
                entry_date,
                exit_date,
                mileage,
                total_cost,
                observations,
                vehicle:vehicle_id(id, license_plate, brand, model, year, fire_station:fire_station_id(id, name, address)),
                maintenance_order_status:order_status_id(id, name, description),
                maintenance_type:maintenance_type_id(id, name, description)
            """.trimIndent()
            
            val orders = client.postgrest["maintenance_order"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("workshop_id", workshopId)
                    }
                }
                .decodeList<MaintenanceOrderDto>()

            val activeStatuses = listOf("pendiente", "en taller", "en espera de repuestos")
            val activeOrders = orders.filter { order ->
                order.maintenance_order_status.name.lowercase() in activeStatuses
            }

            Log.d(TAG, "Órdenes activas: ${activeOrders.size}")
            Result.success(activeOrders.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener órdenes activas: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getAllMaintenanceOrders(workshopId: Int): Result<List<MaintenanceOrder>> {
        return try {
            Log.d(TAG, "Obteniendo TODAS las órdenes para taller ID: $workshopId")
            
            val selectColumns = """
                id,
                entry_date,
                exit_date,
                mileage,
                total_cost,
                observations,
                vehicle:vehicle_id(id, license_plate, brand, model, year, fire_station:fire_station_id(id, name, address)),
                maintenance_order_status:order_status_id(id, name, description),
                maintenance_type:maintenance_type_id(id, name, description)
            """.trimIndent()
            
            val orders = client.postgrest["maintenance_order"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("workshop_id", workshopId)
                    }
                }
                .decodeList<MaintenanceOrderDto>()

            Log.d(TAG, "Total de órdenes: ${orders.size}")
            Result.success(orders.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener todas las órdenes: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getMaintenanceOrderById(orderId: Int): Result<MaintenanceOrderDetail> {
        return try {
            Log.d(TAG, "Obteniendo detalle de orden ID: $orderId")
            
            val selectColumns = """
                id,
                entry_date,
                exit_date,
                mileage,
                total_cost,
                observations,
                vehicle:vehicle_id(id, license_plate, brand, model, year, fire_station:fire_station_id(id, name, address)),
                maintenance_order_status:order_status_id(id, name, description),
                maintenance_type:maintenance_type_id(id, name, description),
                assigned_mechanic:assigned_mechanic_id(id, first_name, last_name, is_active),
                maintenance_task(
                    id,
                    description,
                    cost,
                    task_type:task_type_id(id, name, description),
                    maintenance_task_part(
                        id,
                        quantity_used,
                        cost_per_unit,
                        workshop_inventory:workshop_inventory_id(
                            id,
                            quantity,
                            current_cost,
                            location,
                            workshop_sku,
                            spare_part:spare_part_id(id, name, sku, brand, description)
                        )
                    )
                )
            """.trimIndent()
            
            val orderDto = client.postgrest["maintenance_order"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("id", orderId)
                    }
                }
                .decodeSingle<MaintenanceOrderDetailDto>()

            Log.d(TAG, "Orden obtenida: #${orderDto.id}, Tareas: ${orderDto.maintenance_task.size}")
            Result.success(orderDto.toDomain())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener detalle de orden: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getMaintenanceOrderStatuses(): Result<List<MaintenanceOrderStatus>> {
        return try {
            Log.d(TAG, "Obteniendo estados de órdenes")
            
            val statuses = client.postgrest["maintenance_order_status"]
                .select()
                .decodeList<MaintenanceOrderStatusDto>()
            
            Log.d(TAG, "Estados obtenidos: ${statuses.size}")
            Result.success(statuses.map { it.toDomain() })
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener estados: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getMaintenanceTypes(): Result<List<MaintenanceType>> {
        return try {
            Log.d(TAG, "Obteniendo tipos de mantención")
            
            val types = client.postgrest["maintenance_type"]
                .select()
                .decodeList<MaintenanceTypeDto>()
            
            Log.d(TAG, "Tipos obtenidos: ${types.size}")
            Result.success(types.map { it.toDomain() })
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener tipos de mantención: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getWorkshopMechanics(workshopId: Int): Result<List<Mechanic>> {
        return try {
            Log.d(TAG, "Obteniendo mecánicos del taller ID: $workshopId")
            
            // Buscar usuarios con rol "Mecánico" y workshop_id correspondiente
            val selectColumns = """
                id,
                first_name,
                last_name,
                is_active,
                role:role_id(name)
            """.trimIndent()
            
            val mechanics = client.postgrest["user_profile"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("workshop_id", workshopId)
                        eq("is_active", true)
                    }
                }
                .decodeList<MechanicDto>()
            
            Log.d(TAG, "Mecánicos obtenidos: ${mechanics.size}")
            Result.success(mechanics.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener mecánicos: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getTaskTypes(): Result<List<TaskType>> {
        return try {
            Log.d(TAG, "Obteniendo tipos de tareas")
            
            val types = client.postgrest["task_type"]
                .select()
                .decodeList<TaskTypeDto>()
            
            Log.d(TAG, "Tipos de tareas obtenidos: ${types.size}")
            Result.success(types.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener tipos de tareas: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getWorkshopInventory(workshopId: Int): Result<List<WorkshopInventoryItem>> {
        return try {
            Log.d(TAG, "Obteniendo inventario del taller ID: $workshopId")
            
            val selectColumns = """
                id,
                quantity,
                current_cost,
                location,
                workshop_sku,
                spare_part:spare_part_id(id, name, sku, brand, description)
            """.trimIndent()
            
            val inventory = client.postgrest["workshop_inventory"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("workshop_id", workshopId)
                    }
                }
                .decodeList<WorkshopInventoryDto>()
            
            Log.d(TAG, "Items de inventario obtenidos: ${inventory.size}")
            Result.success(inventory.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener inventario: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun updateMaintenanceOrder(
        orderId: Int,
        statusId: Int,
        maintenanceTypeId: Int,
        assignedMechanicId: String?,
        exitDate: String?,
        observations: String?,
        totalCost: Double?
    ): Result<Unit> {
        return try {
            Log.d(TAG, "Actualizando orden ID: $orderId")
            
            val updateData = UpdateMaintenanceOrderDto(
                order_status_id = statusId,
                maintenance_type_id = maintenanceTypeId,
                assigned_mechanic_id = assignedMechanicId,
                exit_date = exitDate,
                observations = observations,
                total_cost = totalCost
            )
            
            client.postgrest["maintenance_order"]
                .update(updateData) {
                    filter {
                        eq("id", orderId)
                    }
                }
            
            Log.d(TAG, "Orden actualizada exitosamente")
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Error al actualizar orden: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun createMaintenanceTask(
        maintenanceOrderId: Int,
        taskTypeId: Int,
        description: String?,
        cost: Double
    ): Result<MaintenanceTask> {
        return try {
            Log.d(TAG, "Creando tarea para orden ID: $maintenanceOrderId")
            
            val createData = CreateMaintenanceTaskDto(
                task_type_id = taskTypeId,
                maintenance_order_id = maintenanceOrderId,
                description = description,
                cost = cost
            )
            
            val selectColumns = """
                id,
                description,
                cost,
                task_type:task_type_id(id, name, description)
            """.trimIndent()
            
            val taskDto = client.postgrest["maintenance_task"]
                .insert(createData) {
                    select(columns = Columns.raw(selectColumns))
                }
                .decodeSingle<MaintenanceTaskDto>()
            
            Log.d(TAG, "Tarea creada: #${taskDto.id}")
            Result.success(taskDto.toDomain())
        } catch (e: Exception) {
            Log.e(TAG, "Error al crear tarea: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun addPartToTask(
        maintenanceTaskId: Int,
        workshopInventoryId: Int,
        quantityUsed: Int,
        costPerUnit: Double?
    ): Result<Unit> {
        return try {
            Log.d(TAG, "Agregando repuesto a tarea ID: $maintenanceTaskId")
            
            val createData = CreateMaintenanceTaskPartDto(
                maintenance_task_id = maintenanceTaskId,
                workshop_inventory_id = workshopInventoryId,
                quantity_used = quantityUsed,
                cost_per_unit = costPerUnit
            )
            
            client.postgrest["maintenance_task_part"]
                .insert(createData)
            
            // Actualizar inventario (restar cantidad)
            // Nota: Idealmente esto debería ser una transacción
            Log.d(TAG, "Repuesto agregado exitosamente")
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Error al agregar repuesto: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun deleteMaintenanceTask(taskId: Int): Result<Unit> {
        return try {
            Log.d(TAG, "Eliminando tarea ID: $taskId")
            
            // Primero eliminar los repuestos asociados
            client.postgrest["maintenance_task_part"]
                .delete {
                    filter {
                        eq("maintenance_task_id", taskId)
                    }
                }
            
            // Luego eliminar la tarea
            client.postgrest["maintenance_task"]
                .delete {
                    filter {
                        eq("id", taskId)
                    }
                }
            
            Log.d(TAG, "Tarea eliminada exitosamente")
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Error al eliminar tarea: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun removePartFromTask(partId: Int): Result<Unit> {
        return try {
            Log.d(TAG, "Eliminando repuesto ID: $partId")
            
            client.postgrest["maintenance_task_part"]
                .delete {
                    filter {
                        eq("id", partId)
                    }
                }
            
            Log.d(TAG, "Repuesto eliminado exitosamente")
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Error al eliminar repuesto: ${e.message}", e)
            Result.failure(e)
        }
    }
}
