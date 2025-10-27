package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.Vehicle

interface VehiclesRepository {
    suspend fun getVehicles(): Result<List<Vehicle>>
}