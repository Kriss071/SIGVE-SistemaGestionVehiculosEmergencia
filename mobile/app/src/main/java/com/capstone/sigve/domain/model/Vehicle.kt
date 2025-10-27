package com.capstone.sigve.domain.model

import kotlinx.serialization.Serializable

@Serializable
data class Vehicle (
    val id: Int,
    val licensePlate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val engineNumber: String?,
    val vin: String?,
    val mileage: Int?,
    val mileageLastUpdated: String?,
    val oilCapacityLiters: Double?,
    val registrationDate: String?,
    val nextRevisionDate: String?,
    val fireStationId: Int,
    val vehicleTypeId: Int,
    val vehicleStatusId: Int,
    val fuelTypeId: Int?,
    val transmissionTypeId: Int?,
    val oilTypeId: Int?,
    val coolantTypeId: Int?
)