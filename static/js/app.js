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

    // Funcion para manejar el evento de click en las estrellas
    const handleRating = async (negocioId, puntuacion) => {
        try {
            const response = await fetch('/api/valorar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    negocio_id: negocioId,
                    puntuacion: puntuacion
                })
            });

            const data = await response.json();
            if (response.ok) {
                /*alert('¡Gracias por tu valoración!');*/
                showToast("¡Gracias por tu valoración!", "success");
                // Recarga la página para mostrar el ranking actualizado y las nuevas recomendaciones
                window.location.reload(); 
            } else {
                /*alert(`Error: ${data.error}`);*/
                showToast(`${data.error}`, "error");
            }
        } catch (error) {
            console.error("Error al valorar el negocio:", error);
        }
    };

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

            // Nuevo HTML para incluir las estrellas de valoración y el botón de "Ver más"
            card.innerHTML = `
                <img src="static/${imageUrl}" alt="Imagen de ${business.name}">
                <div class="card-content">
                    <h3>${business.name}</h3>
                    <p>${business.category}</p>
                    <p class="ranking">${rankingStars} (${business.ranking})</p>
                    
                    <div class="rating-stars" data-negocio-id="${business.id}">
                        <span class="star" data-value="1">★</span>
                        <span class="star" data-value="2">★</span>
                        <span class="star" data-value="3">★</span>
                        <span class="star" data-value="4">★</span>
                        <span class="star" data-value="5">★</span>
                    </div>

                    <a href="/negocio/${business.id}">Ver más</a>
                </div>
            `;
            grid.appendChild(card);
        });

        // Una vez que las tarjetas se han renderizado, adjunta los event listeners a las estrellas
        setupRatingListeners();
    };

    // Funcion que configura los listeners para las estrellas
    const setupRatingListeners = () => {
        const starContainers = document.querySelectorAll('.rating-stars');
        starContainers.forEach(container => {
            const negocioId = container.dataset.negocioId;
            const stars = container.querySelectorAll('.star');

            stars.forEach(star => {
                star.addEventListener('click', () => {
                    const puntuacion = star.dataset.value;
                    handleRating(negocioId, puntuacion);
                });
            });
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
    
    // Lógica para los botones de categoría
    const categoryButtons = document.querySelectorAll('.category-item');
    categoryButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const category = button.dataset.category;
            getRecommendations(category, "category");
        });
    });

    // Lógica para la barra de búsqueda
    const searchInput = document.querySelector('.search-box input');
    const searchButton = document.querySelector('.search-box button');

    if (searchButton && searchInput) {
        searchButton.addEventListener('click', (e) => {
            e.preventDefault();
            const searchTerm = searchInput.value;
            if (searchTerm.trim() !== "") {                
                getRecommendations(searchTerm, "search");
            }
        });
    }

    const renderPagination = (totalPages, currentPage) => {
    const paginationContainer = document.getElementById('businesses-pagination');
    if (!paginationContainer) return;

    paginationContainer.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const pageLink = document.createElement('a');
        pageLink.href = "#";
        pageLink.textContent = i;
        pageLink.classList.add('page-link');
        if (i === currentPage) {
            pageLink.classList.add('active');
        }
        pageLink.addEventListener('click', (e) => {
            e.preventDefault();
            getAllBusinesses(i); // Carga la página seleccionada
        });
        paginationContainer.appendChild(pageLink);
    }
};

const getAllBusinesses = async (page = 1) => {
    try {
        const response = await fetch(`/api/todos_los_negocios?page=${page}&limit=12`);
        const data = await response.json();

        const grid = document.getElementById('businesses-grid');
        if (grid) {
            grid.innerHTML = '';
            data.businesses.forEach(business => {
                const card = document.createElement('div');
                card.classList.add('business-card');

                // Genera estrellas y URL de la imagen
                const imageUrl = business.image_url || 'https://via.placeholder.com/300x200';
                const rankingStars = '★'.repeat(Math.floor(business.ranking)) +
                                     ((business.ranking % 1 !== 0) ? '½' : '');

                // Inserta el HTML completo de la tarjeta
                card.innerHTML = `
                    <img src="static/${imageUrl}" alt="Imagen de ${business.name}">
                    <div class="card-content">
                        <h3>${business.name}</h3>
                        <p>${business.category}</p>
                        <p class="ranking">${rankingStars} (${business.ranking})</p>
                        
                        <div class="rating-stars" data-negocio-id="${business.id}">
                            <span class="star" data-value="1">★</span>
                            <span class="star" data-value="2">★</span>
                            <span class="star" data-value="3">★</span>
                            <span class="star" data-value="4">★</span>
                            <span class="star" data-value="5">★</span>
                        </div>

                        <a href="/negocio/${business.id}">Ver más</a>
                    </div>
                `;
                grid.appendChild(card);
            });

            // Llama a la función que genera los botones de paginación
            renderPagination(data.total_pages, data.current_page);
            // Vuelve a adjuntar los listeners de las estrellas para las nuevas tarjetas
            setupRatingListeners();
        }

    } catch (error) {
        console.error("Error al obtener todos los negocios:", error);
    }
};


    // Lógica para el enlace "Negocios"
    const businessesLink = document.querySelector('a[href="#negocios"]');
    if (businessesLink) {
        businessesLink.addEventListener('click', (e) => {
            getAllBusinesses(1); // Carga la primera página por defecto
        });
    }


    // --- Lógica Principal de la Aplicación ---

    // Obtiene las recomendaciones personalizadas o populares desde el backend
    /*
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
*/

// Obtiene las recomendaciones personalizadas, populares, por categoría o por búsqueda
    const getRecommendations = async (query = "popular", type = "user_id") => {
        try {
            const response = await fetch(`/api/recomendaciones?${type}=${query}`);
            if (!response.ok) {
                throw new Error('No se pudieron obtener las recomendaciones');
            }
            const recommendations = await response.json();

            const recommendationsWithCoords = recommendations.map(rec => ({
                ...rec,
                lat: rec.lat || (Math.random() * (9.72 - 9.71) + 9.71),
                lng: rec.lng || (Math.random() * (-75.12 - -75.13) + -75.13)
            }));

            renderBusinessCards(recommendationsWithCoords);
            addMarkersToMap(recommendationsWithCoords);

        } catch (error) {
            console.error("Error en la petición de recomendaciones:", error);
            try {
                // Si falla la petición de recomendaciones, intenta obtener los populares
                const response = await fetch('/api/popular_businesses');
                if (!response.ok) {
                    throw new Error('No se pudieron obtener los negocios populares');
                }
                const popularBusinesses = await response.json();
               
                // Muestra los negocios populares
                renderBusinessCards(popularBusinesses);
                addMarkersToMap(popularBusinesses);

            } catch (popularError) {
                console.error("Error al obtener los negocios populares:", popularError);
                // Fallback final: muestra un mensaje al usuario
                const grid = document.querySelector('.recommendations-grid');
                if (grid) {
                    grid.innerHTML = '<p class="no-recom">No se pudieron cargar las recomendaciones.</p>';
                }
            }

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

    // --- Lógica del Chatbot ---
const chatbotButton = document.getElementById('chatbot-button');
const chatbotContainer = document.getElementById('chatbot-container');
const chatbotCloseButton = document.getElementById('chatbot-close-button');
const chatbotMessages = document.getElementById('chatbot-messages');
const chatbotInput = document.getElementById('chatbot-input');
const chatbotSendButton = document.getElementById('chatbot-send-button');

// Muestra/oculta el contenedor del chatbot
if (chatbotButton && chatbotContainer && chatbotCloseButton) {
    chatbotButton.addEventListener('click', () => {
        chatbotContainer.classList.toggle('active');
        if (chatbotContainer.classList.contains('active')) {
            chatbotInput.focus();
        }
    });

    chatbotCloseButton.addEventListener('click', () => {
        chatbotContainer.classList.remove('active');
    });
}

// Función para añadir mensajes al chat
const addMessage = (text, sender) => {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.innerHTML = text;
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight; // Auto-scroll
};

// Función para enviar mensajes al backend
const sendMessage = async () => {
    const userMessage = chatbotInput.value.trim();
    if (userMessage === '') return;

    addMessage(userMessage, 'user');
    chatbotInput.value = '';

    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });
        const data = await response.json();

        // Si la respuesta es una lista de negocios, renderiza las tarjetas
        if (data.type === 'negocios' && data.data && data.data.length > 0) {
            // Prepara el HTML de las tarjetas
            let businessesHtml = 'Aquí tienes algunas recomendaciones: <br><br>';
            data.data.forEach(business => {
                const rankingStars = '★'.repeat(Math.floor(business.promedio_ranking)) + ((business.promedio_ranking % 1 !== 0) ? '½' : '');
                businessesHtml += `
                    <div class="chatbot-card">
                        <img src="${business.imagen_url}" alt="${business.nombre}">
                        <div class="card-content">
                            <h4>${business.nombre}</h4>
                            <p>${business.categoria}</p>
                            <p>${rankingStars} (${business.promedio_ranking})</p>
                            <a href="/negocio/${business._id}" target="_blank">Ver más</a>
                        </div>
                    </div>
                `;
            });
            addMessage(businessesHtml, 'bot');
        } else {
            // Si es un mensaje de texto normal
            addMessage(data.message, 'bot');
        }

    } catch (error) {
        console.error('Error:', error);
        addMessage('Lo siento, hubo un error al conectar con el asistente.', 'bot');
    }
};

if (chatbotSendButton && chatbotInput) {
    chatbotSendButton.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

/* Mensajes emergentes tipo Toast */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`; // aplica clase dinámica
  toast.textContent = message;

  const container = document.getElementById('toast-container');
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, duration);
}

/* FIN */
});
