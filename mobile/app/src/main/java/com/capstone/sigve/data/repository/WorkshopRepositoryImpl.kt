package com.capstone.sigve.data.repository

import android.util.Log
import com.capstone.sigve.data.dto.MaintenanceOrderDto
import com.capstone.sigve.data.dto.WorkshopDto
import com.capstone.sigve.data.mapper.toDomain
import com.capstone.sigve.data.mapper.toDomainList
import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.Workshop
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
            
            // Query con joins - obtenemos todas las órdenes del taller
            // y filtramos por estado activo en el cliente
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
            
            Log.d(TAG, "Columnas de select: $selectColumns")
            
            val orders = client.postgrest["maintenance_order"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("workshop_id", workshopId)
                    }
                }
                .decodeList<MaintenanceOrderDto>()

            Log.d(TAG, "Órdenes obtenidas del servidor: ${orders.size}")
            orders.forEach { order ->
                Log.d(TAG, "Orden #${order.id}: Vehículo=${order.vehicle.license_plate}, Estado=${order.maintenance_order_status.name}")
            }

            // Filtrar en cliente por estados activos
            val activeStatuses = listOf("pendiente", "en taller", "en espera de repuestos")
            val activeOrders = orders.filter { order ->
                val statusName = order.maintenance_order_status.name.lowercase()
                val isActive = statusName in activeStatuses
                Log.d(TAG, "Orden #${order.id}: estado='$statusName', activo=$isActive")
                isActive
            }

            Log.d(TAG, "Órdenes activas después del filtro: ${activeOrders.size}")
            Result.success(activeOrders.toDomainList())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener órdenes: ${e.message}", e)
            e.printStackTrace()
            Result.failure(e)
        }
    }
}

