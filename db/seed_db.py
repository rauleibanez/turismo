from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
# --- Conexión a MongoDB ---
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("No se ha definido la variable de entorno MONGO_URI.")
    
client = MongoClient(mongo_uri) 
db = client[os.getenv('MONGO_DB_NAME')] # El nombre de la base de datos también se lee desde .env


# --- Datos Simulados ---

# Datos de Negocios
negocios_data = [
    {
        '_id': ObjectId('66d6c483d463d12d45a90100'),
        'nombre': 'Restaurante El Fogon',
        'categoria': 'Restaurantes',
        'descripcion': 'Cocina tradicional colombiana en un ambiente acogedor.',
        'promedio_ranking': 4.5,
        'imagen_url': 'img/db_img/1.png',
        'coordenadas': {'lat': 9.712, 'lon': -75.127},
        'telefono': '+57 300 123 4567',
        'email': 'elfogon@example.com',
        'horario_atencion': {
            'lunes': '11:00 AM - 10:00 PM',
            'martes': '11:00 AM - 10:00 PM',
            'miercoles': '11:00 AM - 10:00 PM',
            'jueves': '11:00 AM - 10:00 PM',
            'viernes': '11:00 AM - 11:00 PM',
            'sabado': '11:00 AM - 11:00 PM',
            'domingo': '11:00 AM - 09:00 PM'
        }
    },
    {
        '_id': ObjectId('66d6c483d463d12d45a90101'),
        'nombre': 'Hospedaje La Candelaria',
        'categoria': 'Hospedajes',
        'descripcion': 'Un lugar tranquilo y familiar para descansar en El Carmen.',
        'promedio_ranking': 4.8,
        'imagen_url': 'img/db_img/2.png',
        'coordenadas': {'lat': 9.715, 'lon': -75.130},
        'telefono': '+57 310 987 6543',
        'email': 'lacandelaria@example.com',
        'horario_atencion': {
            'lunes': 'Abierto 24/7',
            'martes': 'Abierto 24/7',
            'miercoles': 'Abierto 24/7',
            'jueves': 'Abierto 24/7',
            'viernes': 'Abierto 24/7',
            'sabado': 'Abierto 24/7',
            'domingo': 'Abierto 24/7'
        }
    },
    {
        '_id': ObjectId('66d6c483d463d12d45a90102'),
        'nombre': 'Parque El Carmen',
        'categoria': 'Sitios Turisticos',
        'descripcion': 'El corazón verde de la ciudad, ideal para un paseo en familia.',
        'promedio_ranking': 4.7,
        'imagen_url': 'img/db_img/3.png',
        'coordenadas': {'lat': 9.710, 'lon': -75.125},
        'telefono': '+57 300 555 1234',
        'email': 'parquecarmen@example.com',
        'horario_atencion': {
            'lunes': '06:00 AM - 09:00 PM',
            'martes': '06:00 AM - 09:00 PM',
            'miercoles': '06:00 AM - 09:00 PM',
            'jueves': '06:00 AM - 09:00 PM',
            'viernes': '06:00 AM - 10:00 PM',
            'sabado': '06:00 AM - 10:00 PM',
            'domingo': '06:00 AM - 09:00 PM'
        }
    },
    {
        '_id': ObjectId('66d6c483d463d12d45a90103'),
        'nombre': 'Bar La Cueva',
        'categoria': 'Bares',
        'descripcion': 'El lugar perfecto para disfrutar de la noche con amigos.',
        'promedio_ranking': 4.2,
        'imagen_url': 'img/db_img/4.png',
        'coordenadas': {'lat': 9.718, 'lon': -75.128},
        'telefono': '+57 320 111 2233',
        'email': 'barlacueva@example.com',
        'horario_atencion': {
            'lunes': 'Cerrado',
            'martes': '05:00 PM - 02:00 AM',
            'miercoles': '05:00 PM - 02:00 AM',
            'jueves': '05:00 PM - 02:00 AM',
            'viernes': '06:00 PM - 03:00 AM',
            'sabado': '06:00 PM - 03:00 AM',
            'domingo': 'Cerrado'
        }
    },
    {
        '_id': ObjectId('66d6c483d463d12d45a90104'),
        'nombre': 'Casa de la Cultura',
        'categoria': 'Sitios Turisticos',
        'descripcion': 'Un centro cultural que celebra las tradiciones de la región.',
        'promedio_ranking': 4.9,
        'imagen_url': 'https://via.placeholder.com/300x200',
        'coordenadas': {'lat': 9.713, 'lon': -75.126},
        'telefono': '+57 300 444 5566',
        'email': 'cultura@example.com',
        'horario_atencion': {
            'lunes': '08:00 AM - 05:00 PM',
            'martes': '08:00 AM - 05:00 PM',
            'miercoles': '08:00 AM - 05:00 PM',
            'jueves': '08:00 AM - 05:00 PM',
            'viernes': '08:00 AM - 04:00 PM',
            'sabado': '09:00 AM - 01:00 PM',
            'domingo': 'Cerrado'
        }
    }
]

# Datos de Usuarios
usuarios_data = [
    {
        '_id': ObjectId('66d6c483d463d12d45a90105'),
        'nombre': 'Carlos Ramirez',
        'email': 'carlos@example.com',
        'password_hash': '12345', # Usa un hash seguro en un entorno real
        'fecha_registro': datetime.now()
    },
    {
        '_id': ObjectId('66d6c483d463d12d45a90106'),
        'nombre': 'Maria Lopez',
        'email': 'maria@example.com',
        'password_hash': '12345',
        'fecha_registro': datetime.now()
    }
]

# Datos de Valoraciones para el motor de recomendaciones
valoraciones_data = [
    # Valoraciones de Carlos (usuario 105)
    {
        'usuario_id': ObjectId('66d6c483d463d12d45a90105'),
        'negocio_id': ObjectId('66d6c483d463d12d45a90100'), # Restaurante El Fogon
        'puntuacion': 5,
        'comentario': '¡Deliciosa comida!'
    },
    {
        'usuario_id': ObjectId('66d6c483d463d12d45a90105'),
        'negocio_id': ObjectId('66d6c483d463d12d45a90102'), # Parque El Carmen
        'puntuacion': 4,
        'comentario': 'Muy bonito para pasar la tarde.'
    },
    # Valoraciones de Maria (usuario 106)
    {
        'usuario_id': ObjectId('66d6c483d463d12d45a90106'),
        'negocio_id': ObjectId('66d6c483d463d12d45a90101'), # Hospedaje La Candelaria
        'puntuacion': 5,
        'comentario': 'Excelente servicio y ambiente.'
    },
    {
        'usuario_id': ObjectId('66d6c483d463d12d45a90106'),
        'negocio_id': ObjectId('66d6c483d463d12d45a90103'), # Bar La Cueva
        'puntuacion': 4,
        'comentario': 'Buena música y buenos tragos.'
    },
    {
        'usuario_id': ObjectId('66d6c483d463d12d45a90106'),
        'negocio_id': ObjectId('66d6c483d463d12d45a90100'), # Restaurante El Fogon
        'puntuacion': 4,
        'comentario': 'Muy bueno, pero un poco lento el servicio.'
    }
]

# --- Funciones de Poblado de la DB ---

def populate_collections():
    """
    Función principal para poblar las colecciones en MongoDB.
    """
    print("Iniciando la población de la base de datos...")

    # Borra las colecciones si ya existen
    db.negocios.drop()
    db.usuarios.drop()
    db.valoraciones.drop()
    print("Colecciones existentes borradas.")

    # Inserta los datos en las colecciones
    db.negocios.insert_many(negocios_data)
    print(f"Insertados {len(negocios_data)} negocios.")

    db.usuarios.insert_many(usuarios_data)
    print(f"Insertados {len(usuarios_data)} usuarios.")

    db.valoraciones.insert_many(valoraciones_data)
    print(f"Insertadas {len(valoraciones_data)} valoraciones.")

    print("\nBase de datos poblada exitosamente. ¡Listo para usar!")

if __name__ == '__main__':
    populate_collections()
