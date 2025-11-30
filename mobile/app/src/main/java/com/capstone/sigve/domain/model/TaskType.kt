package com.capstone.sigve.domain.model

/**
 * Tipo de tarea/trabajo estándar de taller (ej: Cambio de Aceite, Revisión Frenos)
 */
data class TaskType(
    val id: Int,
    val name: String,
    val description: String? = null
)

