package com.capstone.sigve.domain.model

/**
 * Modelo de dominio para el rol del usuario
 */
data class Role(
    val id: Int,
    val name: String,
    val description: String? = null
)

/**
 * Representa las diferentes vistas/módulos de la aplicación según el rol
 */
enum class AppModule {
    ADMIN,          // Para Admin SIGVE
    WORKSHOP,       // Para Admin Taller y Mecánico
    FIRE_STATION    // Para Jefe Cuartel
}

/**
 * Extensión para obtener el módulo correspondiente según el nombre del rol
 * Los nombres deben coincidir con los de la tabla 'role' en la base de datos
 */
fun Role.getAppModule(): AppModule = when (name.lowercase()) {
    "admin sigve" -> AppModule.ADMIN
    "admin taller", "mecánico", "mecanico" -> AppModule.WORKSHOP
    "jefe cuartel" -> AppModule.FIRE_STATION
    else -> AppModule.WORKSHOP // Default a taller si no se reconoce
}

