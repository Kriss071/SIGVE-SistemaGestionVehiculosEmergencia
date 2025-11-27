package com.capstone.sigve.domain.model

data class Vehicle(
    val id: Int,
    val licensePlate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val engineNumber: String? = null,
    val vin: String? = null,
    val mileage: Int? = null,
    val mileageLastUpdated: String? = null,
    val oilCapacityLiters: Double? = null,
    val registrationDate: String? = null,
    val nextRevisionDate: String? = null,
    val fireStationId: Int,
    val vehicleTypeId: Int,
    val vehicleStatusId: Int,
    val fuelTypeId: Int? = null,
    val transmissionTypeId: Int? = null,
    val oilTypeId: Int? = null,
    val coolantTypeId: Int? = null
)