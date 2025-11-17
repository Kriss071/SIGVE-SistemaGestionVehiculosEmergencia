/**
 * Módulo de Geocodificación
 * Proporciona funcionalidad para convertir direcciones en coordenadas geográficas
 * utilizando Nominatim de OpenStreetMap.
 */

const Geocoding = {
    /**
     * URL base de Nominatim (OpenStreetMap)
     */
    NOMINATIM_URL: 'https://nominatim.openstreetmap.org/search',
    
    /**
     * Delay en milisegundos para evitar sobrecarga de la API (rate limiting)
     */
    DELAY_MS: 1000,
    
    /**
     * Última vez que se hizo una petición
     */
    lastRequestTime: 0,
    
    /**
     * Geocodifica una dirección y devuelve las coordenadas
     * @param {string} address - Dirección a geocodificar
     * @returns {Promise<{lat: number, lon: number} | null>} Coordenadas o null si falla
     */
    async geocodeAddress(address) {
        if (!address || address.trim() === '') {
            console.warn('Dirección vacía, no se puede geocodificar');
            return null;
        }
        
        // Implementar rate limiting
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequestTime;
        if (timeSinceLastRequest < this.DELAY_MS) {
            await this.sleep(this.DELAY_MS - timeSinceLastRequest);
        }
        
        this.lastRequestTime = Date.now();
        
        // Construir URL con parámetros
        const params = new URLSearchParams({
            q: address,
            format: 'json',
            limit: 1,
            countrycodes: 'cl', // Limitar a Chile
            addressdetails: 1
        });
        
        try {
            const response = await fetch(`${this.NOMINATIM_URL}?${params}`, {
                headers: {
                    'Accept': 'application/json',
                    'User-Agent': 'SIGVE/1.0' // Nominatim requiere User-Agent
                }
            });
            
            if (!response.ok) {
                console.error('Error en la petición de geocodificación:', response.status);
                return null;
            }
            
            const data = await response.json();
            
            if (data && data.length > 0) {
                const result = data[0];
                return {
                    lat: parseFloat(result.lat),
                    lon: parseFloat(result.lon),
                    display_name: result.display_name
                };
            } else {
                console.warn('No se encontraron resultados para la dirección:', address);
                return null;
            }
        } catch (error) {
            console.error('Error al geocodificar dirección:', error);
            return null;
        }
    },
    
    /**
     * Función auxiliar para esperar un tiempo determinado
     * @param {number} ms - Milisegundos a esperar
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    /**
     * Configura la geocodificación automática para un campo de dirección
     * @param {string} addressInputId - ID del input de dirección
     * @param {string} latitudeInputId - ID del input de latitud (hidden)
     * @param {string} longitudeInputId - ID del input de longitud (hidden)
     * @param {string} buttonId - ID del botón para geocodificar manualmente (opcional)
     */
    setupAddressGeocoding(addressInputId, latitudeInputId, longitudeInputId, buttonId = null) {
        const addressInput = document.getElementById(addressInputId);
        const latitudeInput = document.getElementById(latitudeInputId);
        const longitudeInput = document.getElementById(longitudeInputId);
        
        if (!addressInput || !latitudeInput || !longitudeInput) {
            console.error('No se encontraron los elementos necesarios para geocodificación');
            return;
        }
        
        // ID del botón (dinámico o proporcionado)
        const btnId = buttonId || `${addressInputId}-geocode-btn`;
        
        // Buscar botón existente primero
        let geocodeButton = document.getElementById(btnId);
        
        // Si no existe, crearlo
        if (!geocodeButton) {
            geocodeButton = document.createElement('button');
            geocodeButton.type = 'button';
            geocodeButton.className = 'btn btn-sm btn-outline-secondary mt-2';
            geocodeButton.innerHTML = '<i class="bi bi-geo-alt"></i> Buscar ubicación';
            geocodeButton.id = btnId;
            
            // Insertar después del input de dirección
            addressInput.parentNode.insertBefore(geocodeButton, addressInput.nextSibling);
        } else {
            // Si ya existe, limpiar event listeners anteriores clonándolo
            const newButton = geocodeButton.cloneNode(true);
            geocodeButton.parentNode.replaceChild(newButton, geocodeButton);
            geocodeButton = newButton;
        }
        
        // Agregar evento al botón
        geocodeButton.addEventListener('click', async () => {
            const address = addressInput.value.trim();
            
            if (!address) {
                alert('Por favor ingresa una dirección primero');
                return;
            }
            
            // Mostrar indicador de carga
            const originalText = geocodeButton.innerHTML;
            geocodeButton.disabled = true;
            geocodeButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Buscando...';
            
            try {
                const coords = await Geocoding.geocodeAddress(address);
                
                if (coords) {
                    latitudeInput.value = coords.lat;
                    longitudeInput.value = coords.lon;
                    
                    // Mostrar mensaje de éxito
                    geocodeButton.innerHTML = '<i class="bi bi-check-circle"></i> Ubicación encontrada';
                    geocodeButton.classList.remove('btn-outline-secondary');
                    geocodeButton.classList.add('btn-success');
                    
                    setTimeout(() => {
                        geocodeButton.innerHTML = originalText;
                        geocodeButton.classList.remove('btn-success');
                        geocodeButton.classList.add('btn-outline-secondary');
                        geocodeButton.disabled = false;
                    }, 2000);
                } else {
                    alert('No se pudo encontrar la ubicación. Por favor verifica la dirección e intenta nuevamente.');
                    geocodeButton.innerHTML = originalText;
                    geocodeButton.disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Ocurrió un error al buscar la ubicación');
                geocodeButton.innerHTML = originalText;
                geocodeButton.disabled = false;
            }
        });
        
        // Agregar indicador visual cuando hay coordenadas
        const updateCoordinatesIndicator = () => {
            if (latitudeInput.value && longitudeInput.value) {
                addressInput.classList.add('border-success');
            } else {
                addressInput.classList.remove('border-success');
            }
        };
        
        latitudeInput.addEventListener('change', updateCoordinatesIndicator);
        longitudeInput.addEventListener('change', updateCoordinatesIndicator);
        updateCoordinatesIndicator();
    }
};

// Exportar para uso global
window.Geocoding = Geocoding;

