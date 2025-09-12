document.addEventListener('DOMContentLoaded', () => {

    // Global variable for the map instance
    let map;

    // --- Funciones para la UI y la interactividad ---

    // Manejo del menú de navegación para móviles
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu ul');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('show');
        });
    }

    // Renderiza las tarjetas de negocios en la cuadrícula de recomendaciones
    const renderBusinessCards = (data) => {
        const grid = document.querySelector('.recommendations-grid');
        if (!grid) return;

        grid.innerHTML = '';
        if (!data || data.length === 0) {
            grid.innerHTML = '<p class="no-recom">Inicia sesión o valora negocios para recibir recomendaciones personalizadas.</p>';
            return;
        }

        data.forEach(business => {
            const card = document.createElement('div');
            card.classList.add('business-card');

            // Asumiendo que 'business.image_url' se envía desde el backend
            const imageUrl = business.image_url || 'https://via.placeholder.com/300x200';

            // Genera estrellas basadas en el ranking
            const rankingStars = '★'.repeat(Math.floor(business.ranking)) +
                                ((business.ranking % 1 !== 0) ? '½' : '');

            card.innerHTML = `
                <img src="${imageUrl}" alt="Imagen de ${business.name}">
                <div class="card-content">
                    <h3>${business.name}</h3>
                    <p>${business.category}</p>
                    <p class="ranking">${rankingStars} (${business.ranking})</p>
                    <a href="/negocio/${business.id}">Ver más</a>
                </div>
            `;
            grid.appendChild(card);
        });
    };

    // --- Funciones para el Mapa ---

    // Inicializa el mapa de Leaflet
    const initMap = (coords = [9.712, -75.127]) => {
        const mapContainer = document.getElementById('map-container');
        if (!mapContainer) return;

        if (map) {
            map.remove();
        }

        map = L.map('map-container').setView(coords, 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        map.invalidateSize();
    };

    // Agrega marcadores de negocios al mapa
    const addMarkersToMap = (businesses) => {
        if (!map) return;

        // Limpia marcadores anteriores
        map.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });

        // Crea un marcador para cada negocio
        businesses.forEach(business => {
            if (business.lat && business.lng) {
                L.marker([business.lat, business.lng])
                    .addTo(map)
                    .bindPopup(`<b>${business.name}</b><br>${business.category}`)
                    .openPopup();
            }
        });
    };

    // --- Lógica Principal de la Aplicación ---

    // Obtiene las recomendaciones personalizadas o populares desde el backend
    const getRecommendations = async (userId) => {
        try {
            const response = await fetch(`/api/recomendaciones/${userId}`);
            if (!response.ok) {
                throw new Error('No se pudieron obtener las recomendaciones');
            }
            const recommendations = await response.json();

            // Si la lista de recomendaciones no tiene las coordenadas, usa datos simulados para el mapa.
            // En una app real, esto sería manejado por el backend.
            const recommendationsWithCoords = recommendations.map(rec => ({
                ...rec,
                lat: rec.lat || (Math.random() * (9.72 - 9.71) + 9.71),
                lng: rec.lng || (Math.random() * (-75.12 - -75.13) + -75.13)
            }));

            // Renderiza las tarjetas y agrega los marcadores
            renderBusinessCards(recommendationsWithCoords);
            addMarkersToMap(recommendationsWithCoords);

        } catch (error) {
            console.error("Error en la petición de recomendaciones:", error);
            const popularBusinesses = [
                { name: "Restaurante El Fogon", category: "Restaurantes", ranking: 4.5, image_url: "img/el_fogon.png", lat: 9.712, lng: -75.127 },
                { name: "Hospedaje La Candelaria", category: "Hospedajes", ranking: 4.8, image_url: "img/la_candelaria.png", lat: 9.715, lng: -75.130 },
                { name: "Parque El Carmen", category: "Sitios Turisticos", ranking: 4.7, image_url: "img/parque_carmen.png", lat: 9.710, lng: -75.125 },
                { name: "Bar La Cueva", category: "Bares", ranking: 4.2, image_url: "img/la_cueva.png", lat: 9.718, lng: -75.128 }
            ];
            renderBusinessCards(popularBusinesses);
            addMarkersToMap(popularBusinesses);
        }
    };

    // Ejecuta la lógica principal cuando la página ha cargado
    initMap();

    // Obtiene el ID del usuario inyectado por Flask
    const userId = document.querySelector('body').getAttribute('data-user-id');

    if (userId) {
        getRecommendations(userId);
    } else {
        // Si no hay usuario, carga recomendaciones populares por defecto
        getRecommendations("popular");
    }
});
