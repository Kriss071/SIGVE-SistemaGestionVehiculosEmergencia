package com.capstone.sigve.data.repository

import com.capstone.sigve.data.dto.VehicleDto
import com.capstone.sigve.data.mapper.toDomainList
import com.capstone.sigve.domain.model.Vehicle
import com.capstone.sigve.domain.repository.VehiclesRepository
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.postgrest.postgrest
import javax.inject.Inject

class VehiclesRepositoryImpl @Inject constructor(
    private val client: SupabaseClient
) : VehiclesRepository {

    override suspend fun getVehicles(): Result<List<Vehicle>> {
        return try {
            val vehicleDtos = client.postgrest["vehicle"].select().decodeList<VehicleDto>()
            Result.success(vehicleDtos.toDomainList())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}