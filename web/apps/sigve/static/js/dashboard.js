/**
 * Lógica del Dashboard de SIGVE
 * Inicializa el gráfico de estado de vehículos y el mapa de ubicaciones.
 */

let map = null;
let workshopMarkers = [];
let fireStationMarkers = [];

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar gráfico de vehículos
    const chartElement = document.getElementById('vehiclesChart');
    
    if (chartElement) {
        const availableVehicles = chartElement.dataset.available || 0;
        const inWorkshopVehicles = chartElement.dataset.maintenance || 0;

        const ctx = chartElement.getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Disponibles', 'En Taller'],
                datasets: [{
                    data: [availableVehicles, inWorkshopVehicles],
                    backgroundColor: ['#198754', '#ffc107'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    // Inicializar mapa
    initializeMap();
    
    // Configurar toggles de capas
    setupMapToggles();
});

/**
 * Inicializa el mapa de Leaflet y carga las ubicaciones
 */
function initializeMap() {
    const mapElement = document.getElementById('map');
    
    if (!mapElement) {
        return;
    }

    // Centrar en Santiago, Chile por defecto
    map = L.map('map').setView([-33.4489, -70.6693], 11);

    // Agregar capa de tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Cargar ubicaciones desde la API
    loadMapLocations();
}

/**
 * Carga las ubicaciones de talleres y cuarteles desde la API
 */
function loadMapLocations() {
    const mapLoader = document.getElementById('mapLoader');
    
    fetch('/sigve/api/map-locations/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const locations = data.locations;
                
                // Agregar marcadores de talleres
                locations.workshops.forEach(workshop => {
                    addWorkshopMarker(workshop);
                });
                
                // Agregar marcadores de cuarteles
                locations.fire_stations.forEach(station => {
                    addFireStationMarker(station);
                });
                
                // Ajustar vista del mapa para mostrar todos los marcadores
                fitMapBounds();
                
                // Ocultar loader después de que Leaflet termine de renderizar
                setTimeout(() => {
                    const totalMarkers = workshopMarkers.length + fireStationMarkers.length;
                    
                    if (totalMarkers === 0) {
                        // Si no hay marcadores, mostrar mensaje
                        showNoLocationsMessage();
                    } else {
                        // Si hay marcadores, ocultar el loader
                        if (mapLoader) {
                            // Desactivar pointer events inmediatamente para no bloquear el mapa
                            mapLoader.style.pointerEvents = 'none';
                            mapLoader.style.opacity = '0';
                            
                            // Remover completamente después del fade
                            setTimeout(() => {
                                mapLoader.style.display = 'none';
                            }, 300);
                        }
                    }
                }, 300); // Pequeño delay para que Leaflet termine de renderizar
            } else {
                console.error('Error al cargar ubicaciones:', data.error);
                if (mapLoader) {
                    showErrorMessage('Error al cargar las ubicaciones');
                }
            }
        })
        .catch(error => {
            console.error('Error en la petición de ubicaciones:', error);
            if (mapLoader) {
                showErrorMessage('No se pudo conectar con el servidor');
            }
        });
}

/**
 * Agrega un marcador de taller al mapa
 */
function addWorkshopMarker(workshop) {
    // Icono personalizado para talleres (azul)
    const workshopIcon = L.divIcon({
        className: 'custom-map-marker',
        html: '<div style="background-color: #0d6efd; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;"><i class="bi bi-wrench" style="color: white; font-size: 14px;"></i></div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const marker = L.marker([workshop.latitude, workshop.longitude], { icon: workshopIcon })
        .bindPopup(`
            <div style="min-width: 200px;">
                <h6 class="mb-2"><i class="bi bi-wrench text-primary"></i> ${workshop.name}</h6>
                <p class="mb-1 small"><strong>Dirección:</strong> ${workshop.address}</p>
                ${workshop.phone ? `<p class="mb-1 small"><strong>Teléfono:</strong> ${workshop.phone}</p>` : ''}
                ${workshop.email ? `<p class="mb-0 small"><strong>Email:</strong> ${workshop.email}</p>` : ''}
            </div>
        `)
        .addTo(map);
    
    workshopMarkers.push(marker);
}

/**
 * Agrega un marcador de cuartel al mapa
 */
function addFireStationMarker(station) {
    // Icono personalizado para cuarteles (rojo)
    const fireStationIcon = L.divIcon({
        className: 'custom-map-marker',
        html: '<div style="background-color: #dc3545; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;"><i class="bi bi-fire" style="color: white; font-size: 14px;"></i></div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const marker = L.marker([station.latitude, station.longitude], { icon: fireStationIcon })
        .bindPopup(`
            <div style="min-width: 200px;">
                <h6 class="mb-2"><i class="bi bi-fire text-danger"></i> ${station.name}</h6>
                <p class="mb-1 small"><strong>Dirección:</strong> ${station.address}</p>
                ${station.commune ? `<p class="mb-0 small"><strong>Comuna:</strong> ${station.commune}</p>` : ''}
            </div>
        `)
        .addTo(map);
    
    fireStationMarkers.push(marker);
}

/**
 * Ajusta el zoom del mapa para mostrar todos los marcadores
 */
function fitMapBounds() {
    const allMarkers = [...workshopMarkers, ...fireStationMarkers];
    
    if (allMarkers.length > 0) {
        const group = L.featureGroup(allMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * Configura los toggles para mostrar/ocultar capas
 */
function setupMapToggles() {
    const workshopToggle = document.getElementById('toggle-workshops');
    const fireStationToggle = document.getElementById('toggle-fire-stations');
    
    if (workshopToggle) {
        workshopToggle.addEventListener('change', function() {
            workshopMarkers.forEach(marker => {
                if (this.checked) {
                    map.addLayer(marker);
                } else {
                    map.removeLayer(marker);
                }
            });
        });
    }
    
    if (fireStationToggle) {
        fireStationToggle.addEventListener('change', function() {
            fireStationMarkers.forEach(marker => {
                if (this.checked) {
                    map.addLayer(marker);
                } else {
                    map.removeLayer(marker);
                }
            });
        });
    }
}

/**
 * Muestra un mensaje cuando no hay ubicaciones registradas
 */
function showNoLocationsMessage() {
    const mapLoader = document.getElementById('mapLoader');
    if (mapLoader) {
        mapLoader.innerHTML = `
            <div class="text-center">
                <i class="bi bi-geo-alt display-1 text-muted mb-3"></i>
                <h5 class="text-muted">No hay ubicaciones registradas</h5>
                <p class="text-muted mb-0">
                    Agrega coordenadas a tus talleres y cuarteles para verlos en el mapa
                </p>
            </div>
        `;
        mapLoader.style.display = 'flex';
    }
}

/**
 * Muestra un mensaje de error en el mapa
 */
function showErrorMessage(message) {
    const mapLoader = document.getElementById('mapLoader');
    if (mapLoader) {
        mapLoader.innerHTML = `
            <div class="text-center">
                <i class="bi bi-exclamation-triangle display-1 text-danger mb-3"></i>
                <h5 class="text-danger">Error al cargar el mapa</h5>
                <p class="text-muted mb-3">${message}</p>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> Reintentar
                </button>
            </div>
        `;
        mapLoader.style.display = 'flex';
    }
}