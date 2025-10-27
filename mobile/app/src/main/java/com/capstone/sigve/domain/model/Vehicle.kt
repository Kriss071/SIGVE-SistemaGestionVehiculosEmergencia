package com.capstone.sigve.domain.model

import kotlinx.serialization.Serializable

@Serializable
data class Vehicle (
    val id: Int,
    val license_plate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val engine_number: String?,
    val vin: String?,
    val mileage: Int?,
    val mileage_last_updated: String?,
    val oil_capacity_liters: Double?,
    val registration_date: String?,
    val next_revision_date: String?,
    val fire_station_id: Int,
    val vehicle_type_id: Int,
    val vehicle_status_id: Int,
    val fuel_type_id: Int?,
    val transmission_type_id: Int?,
    val oil_type_id: Int?,
    val coolant_type_id: Int?
)