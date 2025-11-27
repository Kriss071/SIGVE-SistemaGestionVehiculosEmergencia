package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.VehicleDto
import com.capstone.sigve.domain.model.Vehicle

fun VehicleDto.toDomain(): Vehicle {
    return Vehicle(
        id = id,
        licensePlate = license_plate,
        brand = brand,
        model = model,
        year = year,
        engineNumber = engine_number,
        vin = vin,
        mileage = mileage,
        mileageLastUpdated = mileage_last_updated,
        oilCapacityLiters = oil_capacity_liters,
        registrationDate = registration_date,
        nextRevisionDate = next_revision_date,
        fireStationId = fire_station_id,
        vehicleTypeId = vehicle_type_id,
        vehicleStatusId = vehicle_status_id,
        fuelTypeId = fuel_type_id,
        transmissionTypeId = transmission_type_id,
        oilTypeId = oil_type_id,
        coolantTypeId = coolant_type_id
    )
}

fun Vehicle.toDto(): VehicleDto {
    return VehicleDto(
        id = id,
        license_plate = licensePlate,
        brand = brand,
        model = model,
        year = year,
        engine_number = engineNumber,
        vin = vin,
        mileage = mileage,
        mileage_last_updated = mileageLastUpdated,
        oil_capacity_liters = oilCapacityLiters,
        registration_date = registrationDate,
        next_revision_date = nextRevisionDate,
        fire_station_id = fireStationId,
        vehicle_type_id = vehicleTypeId,
        vehicle_status_id = vehicleStatusId,
        fuel_type_id = fuelTypeId,
        transmission_type_id = transmissionTypeId,
        oil_type_id = oilTypeId,
        coolant_type_id = coolantTypeId
    )
}

fun List<VehicleDto>.toDomainList(): List<Vehicle> = map { it.toDomain() }

fun List<Vehicle>.toDtoList(): List<VehicleDto> = map { it.toDto() }

