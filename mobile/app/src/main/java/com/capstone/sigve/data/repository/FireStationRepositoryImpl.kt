package com.capstone.sigve.data.repository

import android.util.Log
import com.capstone.sigve.data.dto.FireStationDto
import com.capstone.sigve.data.dto.FireStationVehicleDto
import com.capstone.sigve.data.mapper.toDomain
import com.capstone.sigve.domain.model.FireStation
import com.capstone.sigve.domain.model.FireStationDashboardStats
import com.capstone.sigve.domain.model.FireStationVehicle
import com.capstone.sigve.domain.repository.FireStationRepository
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.postgrest.postgrest
import io.github.jan.supabase.postgrest.query.Columns
import kotlinx.serialization.Serializable
import javax.inject.Inject

class FireStationRepositoryImpl @Inject constructor(
    private val client: SupabaseClient
) : FireStationRepository {

    companion object {
        private const val TAG = "FireStationRepository"
    }

    override suspend fun getFireStationById(fireStationId: Int): Result<FireStation> {
        return try {
            Log.d(TAG, "Obteniendo cuartel con ID: $fireStationId")
            
            val fireStationDto = client.postgrest["fire_station"]
                .select {
                    filter {
                        eq("id", fireStationId)
                    }
                }
                .decodeSingle<FireStationDto>()

            Log.d(TAG, "Cuartel obtenido: ${fireStationDto.name}")
            Result.success(fireStationDto.toDomain())
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener cuartel: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getFireStationVehicles(fireStationId: Int): Result<List<FireStationVehicle>> {
        return try {
            Log.d(TAG, "Obteniendo vehículos del cuartel ID: $fireStationId")
            
            val selectColumns = """
                id,
                license_plate,
                brand,
                model,
                year,
                mileage,
                next_revision_date,
                vehicle_status:vehicle_status_id(id, name, description),
                vehicle_type:vehicle_type_id(id, name, description)
            """.trimIndent()
            
            val vehicleDtos = client.postgrest["vehicle"]
                .select(columns = Columns.raw(selectColumns)) {
                    filter {
                        eq("fire_station_id", fireStationId)
                    }
                }
                .decodeList<FireStationVehicleDto>()

            // Obtener vehículos con órdenes activas
            val vehiclesWithMaintenanceResult = getVehiclesWithActiveMaintenanceOrders(fireStationId)
            val vehiclesWithMaintenance = vehiclesWithMaintenanceResult.getOrDefault(emptyMap())

            val vehicles = vehicleDtos.map { dto ->
                dto.toDomain(
                    hasActiveMaintenanceOrder = vehiclesWithMaintenance.containsKey(dto.id),
                    currentWorkshopName = vehiclesWithMaintenance[dto.id]
                )
            }

            Log.d(TAG, "Vehículos obtenidos: ${vehicles.size}")
            Result.success(vehicles)
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener vehículos: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getVehiclesWithActiveMaintenanceOrders(fireStationId: Int): Result<Map<Int, String?>> {
        return try {
            Log.d(TAG, "Obteniendo vehículos con órdenes activas del cuartel: $fireStationId")
            
            // Primero obtener los IDs de los vehículos del cuartel
            val vehicleIds = client.postgrest["vehicle"]
                .select(columns = Columns.raw("id")) {
                    filter {
                        eq("fire_station_id", fireStationId)
                    }
                }
                .decodeList<VehicleIdDto>()
                .map { it.id }
            
            if (vehicleIds.isEmpty()) {
                Log.d(TAG, "No hay vehículos en el cuartel")
                return Result.success(emptyMap())
            }
            
            // Consulta para obtener órdenes activas de esos vehículos
            // Usamos una consulta con join para obtener órdenes de vehículos del cuartel
            val selectColumns = """
                vehicle_id,
                workshop:workshop_id(name),
                maintenance_order_status:order_status_id(name),
                vehicle:vehicle_id(fire_station_id)
            """.trimIndent()
            
            // Obtener todas las órdenes y filtrar por vehículos del cuartel en memoria
            // (Supabase no permite filtrar directamente en joins anidados de esta manera)
            val allOrders = client.postgrest["maintenance_order"]
                .select(columns = Columns.raw(selectColumns))
                .decodeList<MaintenanceOrderForVehicleDto>()
            
            // Filtrar por vehículos del cuartel y estados activos
            val activeStatuses = listOf("pendiente", "en taller", "en espera de repuestos")
            val vehiclesInMaintenance = allOrders
                .filter { order ->
                    order.vehicle_id in vehicleIds &&
                    order.maintenance_order_status?.name?.lowercase() in activeStatuses
                }
                .associate { it.vehicle_id to it.workshop?.name }
            
            Log.d(TAG, "Vehículos en mantención: ${vehiclesInMaintenance.size}")
            Result.success(vehiclesInMaintenance)
        } catch (e: Exception) {
            Log.e(TAG, "Error al obtener vehículos en mantención: ${e.message}", e)
            Result.success(emptyMap()) // Retornar vacío en caso de error, no fallar todo
        }
    }

    override suspend fun getFireStationStats(fireStationId: Int): Result<FireStationDashboardStats> {
        return try {
            Log.d(TAG, "Calculando estadísticas del cuartel: $fireStationId")
            
            // Obtener todos los vehículos
            val vehiclesResult = getFireStationVehicles(fireStationId)
            if (vehiclesResult.isFailure) {
                return Result.failure(vehiclesResult.exceptionOrNull()!!)
            }
            
            val vehicles = vehiclesResult.getOrThrow()
            
            // Calcular estadísticas
            val totalVehicles = vehicles.size
            val availableVehicles = vehicles.count { it.isAvailable }
            val inMaintenanceVehicles = vehicles.count { it.isInMaintenance }
            val decommissionedVehicles = vehicles.count { it.vehicleStatus.isDecommissioned }
            val vehiclesNeedingRevision = vehicles.count { it.needsRevisionSoon }
            val activeMaintenanceOrders = vehicles.count { it.hasActiveMaintenanceOrder }
            
            // Agrupar por tipo de vehículo
            val vehiclesByType = vehicles
                .groupBy { it.vehicleType.name }
                .mapValues { it.value.size }

            val stats = FireStationDashboardStats(
                totalVehicles = totalVehicles,
                availableVehicles = availableVehicles,
                inMaintenanceVehicles = inMaintenanceVehicles,
                decommissionedVehicles = decommissionedVehicles,
                vehiclesNeedingRevision = vehiclesNeedingRevision,
                vehiclesByType = vehiclesByType,
                activeMaintenanceOrders = activeMaintenanceOrders
            )

            Log.d(TAG, "Estadísticas calculadas: total=$totalVehicles, disponibles=$availableVehicles")
            Result.success(stats)
        } catch (e: Exception) {
            Log.e(TAG, "Error al calcular estadísticas: ${e.message}", e)
            Result.failure(e)
        }
    }
}

// DTOs auxiliares para consultas internas
@Serializable
private data class MaintenanceOrderForVehicleDto(
    val vehicle_id: Int,
    val workshop: WorkshopNameDto? = null,
    val maintenance_order_status: StatusNameDto? = null,
    val vehicle: VehicleFireStationDto? = null
)

@Serializable
private data class WorkshopNameDto(val name: String)

@Serializable
private data class StatusNameDto(val name: String)

@Serializable
private data class VehicleIdDto(val id: Int)

@Serializable
private data class VehicleFireStationDto(val fire_station_id: Int)

