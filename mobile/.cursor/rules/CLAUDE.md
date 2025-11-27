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
│       └── vehicles/     # Use cases de vehículos
├── ui/
│   ├── auth/             # Feature de autenticación
│   ├── common/           # Componentes compartidos
│   ├── navigation/       # Configuración de navegación
│   ├── settings/         # Feature de configuración
│   ├── theme/            # Tema de la aplicación (colores, tipografía)
│   └── vehicles/         # Feature de vehículos
├── MainActivity.kt
└── SigveApplication.kt
```

---

## Convenciones de Código

### Nombrado
- **Clases**: PascalCase (`VehiclesViewModel`, `AuthRepository`)
- **Funciones**: camelCase (`loadVehicles`, `onLoginClicked`)
- **Constantes**: SCREAMING_SNAKE_CASE (`THEME_KEY`, `CUSTOM_PRIMARY`)
- **Paquetes**: minúsculas sin separadores (`mainScreenBottomNav`)
- **Archivos Composable**: PascalCase igual que la función principal (`VehiclesScreen.kt`)
- **UiState**: Sufijo `UiState` para clases de estado (`LoginUiState`, `VehiclesUiState`)

### ViewModels
- Usar anotación `@HiltViewModel`
- Inyectar dependencias vía constructor con `@Inject`
- Exponer estado UI como `mutableStateOf` o `StateFlow`
- Los métodos públicos deben empezar con `on` para eventos (`onLoginClicked`, `onEmailChange`)

```kotlin
@HiltViewModel
class ExampleViewModel @Inject constructor(
    private val repository: ExampleRepository
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
            val data = client.postgrest["table"].select().decodeList<Item>()
            Result.success(data)
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

```kotlin
// data/dto/VehicleDto.kt
@Serializable
data class VehicleDto(
    val id: Int,
    val license_plate: String,
    val brand: String,
    val model: String
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

### Configuración
- Usar Navigation Compose
- Definir rutas como `sealed class` con `data object`
- Navegación principal en `AppNavigation.kt`
- Bottom Navigation en `MainScreenNavigation.kt`

```kotlin
sealed class ExampleRoute(val route: String) {
    data object Home: ExampleRoute("home_screen")
    data object Detail: ExampleRoute("detail_screen/{id}")
}
```

### Bottom Navigation
- Definir ítems en `BottomNavDestinations.kt`
- Usar `BottomNavItem` data class

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

### Módulos instalados
- `Auth` para autenticación
- `Postgrest` para base de datos

### Patrón de uso
```kotlin
// Autenticación
client.auth.signInWith(Email) {
    email = "user@example.com"
    password = "password"
}

// Consultas
client.postgrest["table_name"].select().decodeList<Model>()
```

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

- **Código**: Inglés (nombres de clases, funciones, variables)
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

---

## Features Actuales

- [x] Autenticación (Login)
- [x] Listado de vehículos
- [x] Configuración de tema (claro/oscuro)
- [x] Personalización de colores
- [ ] Mantenciones
- [ ] Gestión de taller
- [ ] Detalle de vehículo
- [ ] Agregar vehículo

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

