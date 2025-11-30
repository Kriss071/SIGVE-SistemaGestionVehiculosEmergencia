# Reglas del Proyecto SIGVE Mobile

## Descripción del Proyecto
SIGVE (Sistema de Gestión de Vehículos de Emergencia) es una aplicación Android nativa desarrollada con Kotlin y Jetpack Compose para la gestión de vehículos de emergencia de bomberos. Utiliza Supabase como backend.

---

## Arquitectura

### Patrón Arquitectónico
- **Clean Architecture** con separación en capas: `data`, `domain`, `ui`
- **MVVM** (Model-View-ViewModel) para la capa de presentación
- **Inyección de Dependencias** con Hilt

### Estructura de Directorios
```
com.capstone.sigve/
├── data/
│   ├── dto/              # Data Transfer Objects (DTOs para Supabase)
│   ├── mapper/           # Mappers DTO <-> Domain
│   ├── repository/       # Implementaciones de repositorios
│   └── seeds/            # Seeds de base de datos (SQL)
├── di/                   # Módulos de Hilt
├── domain/
│   ├── model/            # Modelos de dominio puros (sin anotaciones)
│   ├── repository/       # Interfaces de repositorios
│   └── usecase/          # Casos de uso organizados por feature
│       ├── auth/         # Use cases de autenticación
│       ├── settings/     # Use cases de configuración
│       ├── vehicles/     # Use cases de vehículos
│       └── workshop/     # Use cases de taller
├── ui/
│   ├── admin/            # Módulo Admin SIGVE
│   │   ├── navigation/   # Navegación del módulo Admin
│   │   └── AdminHomeScreen.kt
│   ├── auth/             # Feature de autenticación
│   ├── common/           # Componentes compartidos
│   ├── firestation/      # Módulo Jefe de Cuartel (Fire Station)
│   │   ├── navigation/   # Navegación del módulo Fire Station
│   │   └── FireStationHomeScreen.kt
│   ├── navigation/       # Navegación raíz de la app
│   ├── settings/         # Feature de configuración (compartido)
│   ├── workshop/         # Módulo Taller (Admin Taller + Mecánico)
│   │   ├── navigation/   # Navegación del módulo Workshop
│   │   ├── WorkshopHomeScreen.kt
│   │   ├── WorkshopViewModel.kt
│   │   └── WorkshopUiState.kt
│   ├── theme/            # Tema de la aplicación
│   └── vehicles/         # [DEPRECADO] - Migrar a módulos específicos
├── MainActivity.kt
└── SigveApplication.kt
```

---

## Sistema de Roles y Módulos

### Roles de Usuario (desde BD tabla `role`)
| Rol | Módulo | Descripción |
|-----|--------|-------------|
| Admin SIGVE | ADMIN | Administración global del sistema |
| Admin Taller | WORKSHOP | Gestión del taller mecánico |
| Mecánico | WORKSHOP | Trabajo en mantenciones |
| Jefe Cuartel | FIRE_STATION | Gestión de vehículos del cuartel |

### Modelo de Rol
```kotlin
// El rol se obtiene de la BD mediante join con user_profile
data class Role(
    val id: Int,
    val name: String,       // "Admin SIGVE", "Admin Taller", "Mecánico", "Jefe Cuartel"
    val description: String?
)

// Determinar módulo según nombre del rol
fun Role.getAppModule(): AppModule = when (name.lowercase()) {
    "admin sigve" -> AppModule.ADMIN
    "admin taller", "mecánico", "mecanico" -> AppModule.WORKSHOP
    "jefe cuartel" -> AppModule.FIRE_STATION
    else -> AppModule.WORKSHOP
}
```

### Rutas de Navegación
```kotlin
sealed class RootNavRoute(val route: String) {
    data object Login : RootNavRoute("login_screen")
    data object AdminModule : RootNavRoute("admin_module")
    data object WorkshopModule : RootNavRoute("workshop_module")
    data object FireStationModule : RootNavRoute("fire_station_module")
}
```

---

## Convenciones de Código

### Nombrado
- **Clases**: PascalCase (`VehiclesViewModel`, `AuthRepository`)
- **Funciones**: camelCase (`loadVehicles`, `onLoginClicked`)
- **Constantes**: SCREAMING_SNAKE_CASE (`THEME_KEY`, `CUSTOM_PRIMARY`)
- **Paquetes**: minúsculas sin separadores (`firestation`, `workshop`)
- **Archivos Composable**: PascalCase igual que la función principal (`VehiclesScreen.kt`)
- **UiState**: Sufijo `UiState` para clases de estado (`LoginUiState`, `VehiclesUiState`)

### ViewModels
- Usar anotación `@HiltViewModel`
- Inyectar Use Cases vía constructor con `@Inject`
- Exponer estado UI como `mutableStateOf` o `StateFlow`
- Los métodos públicos deben empezar con `on` para eventos (`onLoginClicked`, `onEmailChange`)

```kotlin
@HiltViewModel
class ExampleViewModel @Inject constructor(
    private val getDataUseCase: GetDataUseCase
) : ViewModel() {
    var uiState by mutableStateOf(ExampleUiState())
        private set
    
    fun onActionClicked() {
        viewModelScope.launch { /* lógica */ }
    }
}
```

### UiState
- Usar `data class` inmutables
- Incluir campos típicos: `isLoading`, `error`, `data`

```kotlin
data class ExampleUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val data: List<Item> = emptyList()
)
```

### Repositorios
- Definir interfaz en `domain/repository/`
- Implementación en `data/repository/` con sufijo `Impl`
- Retornar `Result<T>` para manejar éxito/error
- Usar `@Inject constructor` para DI

```kotlin
// domain/repository/ExampleRepository.kt
interface ExampleRepository {
    suspend fun getData(): Result<List<Item>>
}

// data/repository/ExampleRepositoryImpl.kt
class ExampleRepositoryImpl @Inject constructor(
    private val client: SupabaseClient
) : ExampleRepository {
    override suspend fun getData(): Result<List<Item>> {
        return try {
            val dtos = client.postgrest["table"].select().decodeList<ItemDto>()
            Result.success(dtos.toDomainList())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Modelos de Dominio
- Ubicar en `domain/model/`
- Modelos puros sin anotaciones de serialización
- Nombres de campos en camelCase

```kotlin
// domain/model/Vehicle.kt
data class Vehicle(
    val id: Int,
    val licensePlate: String,
    val brand: String,
    val model: String
)
```

### DTOs (Data Transfer Objects)
- Ubicar en `data/dto/`
- Usar `@Serializable` para interacción con Supabase
- Nombres de campos en snake_case para coincidir con la base de datos
- Para joins, incluir el DTO relacionado como propiedad

```kotlin
// data/dto/UserProfileDto.kt
@Serializable
data class UserProfileDto(
    val id: String,
    val first_name: String,
    val role: RoleDto,  // Join con tabla role
    val workshop_id: Int? = null
)
```

### Mappers
- Ubicar en `data/mapper/`
- Funciones de extensión para conversión DTO <-> Domain
- Incluir funciones para listas

```kotlin
// data/mapper/VehicleMapper.kt
fun VehicleDto.toDomain(): Vehicle { /* ... */ }
fun Vehicle.toDto(): VehicleDto { /* ... */ }
fun List<VehicleDto>.toDomainList(): List<Vehicle> = map { it.toDomain() }
```

### Use Cases
- Ubicar en `domain/usecase/` organizados por feature
- Usar `@Inject constructor` para DI
- Implementar `operator fun invoke()` para uso idiomático

```kotlin
class GetVehiclesUseCase @Inject constructor(
    private val vehiclesRepository: VehiclesRepository
) {
    suspend operator fun invoke(): Result<List<Vehicle>> {
        return vehiclesRepository.getVehicles()
    }
}
```

---

## Jetpack Compose

### Composables
- Usar nombres en PascalCase
- Recibir ViewModel como parámetro con valor por defecto `hiltViewModel()`
- Derivar estado con `derivedStateOf` o `collectAsState`

```kotlin
@Composable
fun ExampleScreen(viewModel: ExampleViewModel = hiltViewModel()) {
    val uiState by remember { derivedStateOf { viewModel.uiState } }
    // UI
}
```

### Componentes Reutilizables
- Ubicar en `ui/common/`
- Parámetros explícitos, evitar hardcodear valores
- Documentar parámetros importantes

### Temas
- Esquema de colores en `Theme.kt`
- Tipografía en `Type.kt`
- Usar `MaterialTheme.colorScheme` y `MaterialTheme.typography`
- El color principal de la app es rojo bomberos: `Color(0xFFDF2532)`

---

## Navegación

### Estructura de Navegación
```
AppNavigation (Raíz)
├── LoginScreen
├── AdminNavigation (Admin SIGVE)
│   ├── AdminHomeScreen
│   └── SettingsScreen
├── WorkshopNavigation (Admin Taller + Mecánico)
│   ├── WorkshopHomeScreen
│   ├── MaintenanceScreen (TODO)
│   ├── InventoryScreen (TODO)
│   └── SettingsScreen
└── FireStationNavigation (Jefe Cuartel)
    ├── FireStationHomeScreen
    ├── VehiclesScreen (TODO)
    ├── HistoryScreen (TODO)
    └── SettingsScreen
```

### Configuración
- Usar Navigation Compose
- Definir rutas como `sealed class` con `data object`
- Cada módulo tiene su propia navegación interna

```kotlin
sealed class WorkshopNavRoute(val route: String, val title: String, val icon: ImageVector) {
    data object Home : WorkshopNavRoute("workshop_home", "Inicio", Icons.Default.Home)
    data object Maintenance : WorkshopNavRoute("workshop_maintenance", "Mantenciones", Icons.Default.Build)
    
    companion object {
        val items = listOf(Home, Maintenance, Inventory, Settings)
    }
}
```

---

## Autenticación

### Flujo de Login
1. Usuario ingresa credenciales
2. `LoginUseCase` autentica con Supabase Auth
3. Se obtiene `UserProfile` con join a tabla `role`
4. Se determina el módulo según `role.name`
5. Se navega al módulo correspondiente

### Query con Join para UserProfile
```kotlin
client.postgrest["user_profile"]
    .select(columns = Columns.raw("*, role(*)")) {
        filter { eq("id", userId) }
    }
    .decodeSingle<UserProfileDto>()
```

### Cierre de Sesión
- Cada módulo tiene botón de logout en el menú
- `LogoutUseCase` cierra sesión en Supabase
- Se navega de vuelta a `LoginScreen`

---

## Inyección de Dependencias (Hilt)

### Módulos
- Ubicar en `di/`
- Anotar con `@Module` y `@InstallIn(SingletonComponent::class)`
- Usar `@Provides` y `@Singleton` para dependencias

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(client: SupabaseClient): Repository {
        return RepositoryImpl(client)
    }
}
```

---

## Supabase

### Configuración
- URL y Key en `local.properties` (NO commitear)
- Acceder via `BuildConfig.SUPABASE_URL` y `BuildConfig.SUPABASE_KEY`

### Tablas Principales
| Tabla | Descripción |
|-------|-------------|
| `user_profile` | Perfiles de usuario con rol |
| `role` | Catálogo de roles (Admin SIGVE, Admin Taller, Mecánico, Jefe Cuartel) |
| `vehicle` | Vehículos de emergencia |
| `fire_station` | Cuarteles de bomberos |
| `workshop` | Talleres mecánicos |
| `maintenance_order` | Órdenes de mantención |
| `maintenance_order_status` | Estados de órdenes (Pendiente, En Taller, En Espera de Repuestos, Completada) |
| `maintenance_type` | Tipos de mantención |

### Patrón de uso con Joins
```kotlin
// Select con foreign key join simple
client.postgrest["user_profile"]
    .select(columns = Columns.raw("*, role(*)")) {
        filter { eq("id", userId) }
    }
    .decodeSingle<UserProfileDto>()

// Select con múltiples joins anidados
client.postgrest["maintenance_order"]
    .select(columns = Columns.raw("""
        id, entry_date, mileage,
        vehicle:vehicle_id(id, license_plate, brand, model, year, 
            fire_station:fire_station_id(id, name)),
        maintenance_order_status:order_status_id(id, name),
        maintenance_type:maintenance_type_id(id, name)
    """)) {
        filter { eq("workshop_id", workshopId) }
    }
    .decodeList<MaintenanceOrderDto>()
```

---

## Módulo Workshop (Taller)

### Funcionalidades Implementadas
- Mostrar nombre del taller del usuario
- Listar vehículos con órdenes activas
- Estados activos: "Pendiente", "En Taller", "En Espera de Repuestos"

### Modelos de Dominio
```kotlin
data class Workshop(val id: Int, val name: String, ...)
data class MaintenanceOrder(val id: Int, val vehicle: VehicleSummary, val status: MaintenanceOrderStatus, ...)
data class MaintenanceOrderStatus(val id: Int, val name: String) {
    val isActive: Boolean get() = name in listOf("Pendiente", "En Taller", "En Espera de Repuestos")
}
data class VehicleSummary(val licensePlate: String, val brand: String, val fireStation: FireStation?)
```

### Use Cases
- `GetWorkshopByIdUseCase` - Obtener información del taller
- `GetActiveMaintenanceOrdersUseCase` - Obtener órdenes activas del taller

---

## DataStore Preferences

### Uso
- Para persistencia de configuraciones locales (tema, colores)
- Definir keys con `stringPreferencesKey` o `longPreferencesKey`
- Exponer datos como `Flow<T>`

---

## Dependencias Principales

| Librería | Propósito |
|----------|-----------|
| Jetpack Compose | UI declarativa |
| Hilt | Inyección de dependencias |
| Navigation Compose | Navegación |
| DataStore Preferences | Preferencias locales |
| Supabase | Backend (Auth + Database) |
| Ktor | Cliente HTTP para Supabase |
| Kotlinx Serialization | Serialización JSON |

---

## Configuración del Proyecto

- **Min SDK**: 24 (Android 7.0)
- **Target/Compile SDK**: 35
- **JVM Target**: 11
- **Kotlin**: 2.0.21
- **Compose BOM**: 2024.04.01

---

## Idioma

- **Código**: Inglés (nombres de clases, funciones, variables, paquetes)
- **UI/Strings**: Español (textos visibles al usuario)
- **Comentarios**: Español preferido

---

## Buenas Prácticas

1. **No commitear `local.properties`** - contiene credenciales
2. **Siempre usar interfaces** para repositorios
3. **Manejar errores** con `Result<T>` y mostrar mensajes apropiados
4. **Estados de UI** deben incluir `isLoading` y `error`
5. **Evitar colores hardcodeados** - usar `MaterialTheme.colorScheme`
6. **Composables pequeños** - extraer componentes reutilizables
7. **Usar `remember`** para estados locales en Composables
8. **LaunchedEffect** para efectos secundarios en Compose
9. **Usar Use Cases** para lógica de negocio entre ViewModel y Repository
10. **Roles desde BD** - Obtener roles dinámicamente de la tabla `role`

---

## Features Actuales

### Implementado ✅
- [x] Autenticación (Login con roles desde BD)
- [x] Navegación basada en roles (Admin, Workshop, FireStation)
- [x] Configuración de tema (claro/oscuro/sistema)
- [x] Personalización de colores
- [x] Estructura de 3 módulos principales
- [x] Logout por módulo
- [x] Join con tabla role para obtener nombre del rol
- [x] **Workshop**: Pantalla de inicio con nombre del taller
- [x] **Workshop**: Listado de vehículos con órdenes activas

### Pendiente 📋
- [ ] **Admin SIGVE**: Gestión global del sistema
- [ ] **Workshop**: Detalle de orden de mantención
- [ ] **Workshop**: Crear/editar órdenes
- [ ] **Workshop**: Inventario de repuestos
- [ ] **FireStation**: Listado de vehículos del cuartel
- [ ] **FireStation**: Historial de mantenciones
- [ ] Detalle de vehículo
- [ ] Agregar/editar vehículo

### Deprecado ⚠️
- `ui/vehicles/` - Migrar funcionalidad a módulos específicos
- `ui/taller/` - Renombrado a `ui/workshop/`
- `ui/cuartel/` - Renombrado a `ui/firestation/`

---

## Comandos Útiles

```bash
# Compilar debug APK
./gradlew assembleDebug

# Ejecutar tests unitarios
./gradlew test

# Limpiar build
./gradlew clean
```
