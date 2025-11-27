package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

@Serializable
data class VehicleDto(
    val id: Int,
    val license_plate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val engine_number: String? = null,
    val vin: String? = null,
    val mileage: Int? = null,
    val mileage_last_updated: String? = null,
    val oil_capacity_liters: Double? = null,
    val registration_date: String? = null,
    val next_revision_date: String? = null,
    val fire_station_id: Int,
    val vehicle_type_id: Int,
    val vehicle_status_id: Int,
    val fuel_type_id: Int? = null,
    val transmission_type_id: Int? = null,
    val oil_type_id: Int? = null,
    val coolant_type_id: Int? = null
)

