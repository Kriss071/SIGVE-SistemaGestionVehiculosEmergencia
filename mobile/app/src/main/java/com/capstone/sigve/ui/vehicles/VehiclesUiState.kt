package com.capstone.sigve.ui.vehicles

import com.capstone.sigve.domain.model.Vehicle

data class VehiclesUiState(
    val isLoading: Boolean = false,
    val vehicles: List<Vehicle> = emptyList(),
    val error: String? = null
)