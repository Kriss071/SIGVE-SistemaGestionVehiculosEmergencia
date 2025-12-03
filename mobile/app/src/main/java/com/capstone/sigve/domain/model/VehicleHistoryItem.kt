package com.capstone.sigve.domain.model

import java.text.SimpleDateFormat
import java.util.Locale

/**
 * Representa un item del historial de un vehículo
 * Puede ser un cambio de estado o una orden de mantención
 */
sealed class VehicleHistoryItem {
    abstract val date: String
    abstract val timestamp: Long
    
    /**
     * Cambio de estado del vehículo
     */
    data class StatusChange(
        val statusLog: VehicleStatusLog
    ) : VehicleHistoryItem() {
        override val date: String = statusLog.changeDate
        override val timestamp: Long = parseTimestamp(statusLog.changeDate)
    }
    
    /**
     * Orden de mantención
     */
    data class MaintenanceOrder(
        val order: VehicleMaintenanceOrderHistory
    ) : VehicleHistoryItem() {
        override val date: String = order.entryDate
        override val timestamp: Long = parseTimestamp(order.entryDate)
    }
    
    companion object {
        private fun parseTimestamp(dateString: String): Long {
            return try {
                // Intentar diferentes formatos de fecha
                val formats = listOf(
                    "yyyy-MM-dd HH:mm:ss",
                    "yyyy-MM-dd'T'HH:mm:ss",
                    "yyyy-MM-dd"
                )
                
                for (format in formats) {
                    try {
                        val sdf = SimpleDateFormat(format, Locale.getDefault())
                        val date = sdf.parse(dateString)
                        if (date != null) {
                            return date.time
                        }
                    } catch (e: Exception) {
                        continue
                    }
                }
                0L
            } catch (e: Exception) {
                0L
            }
        }
    }
}

/**
 * Historial completo de un vehículo
 */
data class VehicleHistory(
    val vehicleId: Int,
    val vehicleLicensePlate: String,
    val vehicleDisplayName: String,
    val items: List<VehicleHistoryItem>
) {
    val sortedItems: List<VehicleHistoryItem>
        get() = items.sortedByDescending { it.timestamp }
}

