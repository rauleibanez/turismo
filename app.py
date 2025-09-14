from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from model.recommendation_engine import train_model, recommend_for_user 
from datetime import datetime

load_dotenv()

# --- Configuración de Flask ---
app = Flask(__name__)
# ¡IMPORTANTE! Cambia esta clave en producción
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# --- Conexión a MongoDB ---
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("No se ha definido la variable de entorno MONGO_URI.")
    
client = MongoClient(mongo_uri) 
db = client[os.getenv('MONGO_DB_NAME')] # El nombre de la base de datos también se lee desde .env

# Entrenar el modelo al iniciar la aplicación
item_similarity_df = train_model()

# --- Rutas de la Aplicación ---
@app.route('/')
def home():
    user_id = session.get('user_id')
    username = session.get('username')
    recommendations = []

    if user_id:
        user_id_obj = ObjectId(user_id)
        recommendations = recommend_for_user(user_id_obj, item_similarity_df)
    else:
        # Muestra los negocios más populares si no hay un usuario logueado
        recommendations = list(db.negocios.find().sort('promedio_ranking', -1).limit(5))

    # Convertir a un formato JSON serializable para Jinja2
    recommendations_for_template = [
        {
            'id': str(b['_id']),
            'name': b['nombre'],
            'category': b['categoria'],
            'ranking': b.get('promedio_ranking', 0),
            'image_url': b.get('imagen_url', 'https://via.placeholder.com/300x200'),
            'lat': b.get('coordenadas', {}).get('lat'),
            'lng': b.get('coordenadas', {}).get('lon')
        } for b in recommendations
    ]

    return render_template('index.html', recommendations=recommendations_for_template, user_id=user_id, username=username)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user = db.usuarios.find_one({'email': email})

        # Usar check_password_hash en un entorno real
        if user and user['password_hash'] == password:
            session['user_id'] = str(user['_id'])
            # Guarda el nombre del usuario en la sesión
            session['username'] = user['nombre']
            return jsonify({"message": "Inicio de sesión exitoso", "user_id": str(user['_id'])}), 200
        return jsonify({"message": "Credenciales inválidas"}), 401
    return render_template("login.html", titulo= "Login")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home')) # Redirige a la página principal

# --- Endpoint de API para el frontend (si se necesita una llamada asíncrona) ---

@app.route('/api/valorar', methods=['POST'])
def valorar_negocio():
    """
    Ruta para que un usuario valore un negocio.
    Recibe el ID del negocio, la puntuación y el ID del usuario de la sesión.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Debes iniciar sesión para valorar un negocio."}), 401

    data = request.json
    negocio_id = data.get('negocio_id')
    puntuacion = data.get('puntuacion')

    if not negocio_id or not puntuacion:
        return jsonify({"error": "Faltan datos de la valoración."}), 400

    try:
        # Asegúrate de que el ID del negocio y la puntuación sean válidos
        negocio_id_obj = ObjectId(negocio_id)
        puntuacion = int(puntuacion)

        if not 1 <= puntuacion <= 5:
            return jsonify({"error": "La puntuación debe ser entre 1 y 5."}), 400

        # Insertar o actualizar la valoración del usuario
        db.valoraciones.update_one(
            {'usuario_id': ObjectId(user_id), 'negocio_id': negocio_id_obj},
            {'$set': {'puntuacion': puntuacion}},
            upsert=True # Si no existe, lo crea
        )
        
        # Calcular y actualizar el promedio del negocio
        valoraciones_negocio = list(db.valoraciones.find({'negocio_id': negocio_id_obj}))
        if valoraciones_negocio:
            total_puntuaciones = sum(v['puntuacion'] for v in valoraciones_negocio)
            promedio = round(total_puntuaciones / len(valoraciones_negocio), 1)

            db.negocios.update_one(
                {'_id': negocio_id_obj},
                {'$set': {'promedio_ranking': promedio}}
            )

        # Volver a entrenar el modelo después de una nueva valoración
        global item_similarity_df
        item_similarity_df = train_model()

        return jsonify({"message": "Valoración guardada y ranking actualizado."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recomendaciones')
def get_recommendations_api():
    try:
        user_id = request.args.get('user_id')
        category = request.args.get('category')
        search_term = request.args.get('search')
        
        recommendations = []
        if user_id:
            if user_id == "popular":
                recommendations = list(db.negocios.find().sort('promedio_ranking', -1).limit(5))
            else:
                user_id_obj = ObjectId(user_id)
                recommendations = recommend_for_user(user_id_obj, item_similarity_df)
        elif category:
            recommendations = list(db.negocios.find({'categoria': category}).limit(10))
        elif search_term:
            # Filtra por término de búsqueda (nombre o descripción)
            # '$regex' permite buscar un texto dentro de un campo.
            # '$options: 'i'' hace que la búsqueda no distinga mayúsculas y minúsculas.
            recommendations = list(db.negocios.find({
                '$or': [
                    {'nombre': {'$regex': search_term, '$options': 'i'}},
                    {'descripcion': {'$regex': search_term, '$options': 'i'}}
                ]
            }).limit(10))
        else:
            return jsonify({"error": "Parámetros de búsqueda no válidos"}), 400

        # ... (el resto de tu lógica para convertir recomendaciones a JSON) ...
        recommendations_json = [
            {
                'id': str(b['_id']),
                'name': b['nombre'],
                'category': b['categoria'],
                'ranking': b.get('promedio_ranking', 0),
                'image_url': b.get('imagen_url', 'https://via.placeholder.com/300x200'),
                'lat': b.get('coordenadas', {}).get('lat'),
                'lng': b.get('coordenadas', {}).get('lon')
            } for b in recommendations
        ]
        return jsonify(recommendations_json), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos_los_negocios')
def get_all_businesses():
    """
    Ruta para obtener todos los negocios de la base de datos con paginación.
    """
    try:
        # Obtiene los parámetros 'page' y 'limit' de la URL
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Calcula la cantidad de documentos a saltar (skip)
        skip = (page - 1) * limit

        # Obtiene el total de negocios para calcular las páginas
        total_businesses = db.negocios.count_documents({})
        
        # Realiza la consulta con skip y limit
        businesses = list(db.negocios.find({}).skip(skip).limit(limit))

        businesses_json = [
            {
                'id': str(b['_id']),
                'name': b['nombre'],
                'category': b['categoria'],
                'ranking': b.get('promedio_ranking', 0),
                'image_url': b.get('imagen_url', 'https://via.placeholder.com/300x200'),
                'lat': b.get('coordenadas', {}).get('lat'),
                'lng': b.get('coordenadas', {}).get('lon')
            } for b in businesses
        ]

        # Devuelve los datos junto con la información de paginación
        return jsonify({
            "businesses": businesses_json,
            "total_pages": (total_businesses + limit - 1) // limit,
            "current_page": page
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/negocio/<negocio_id>')
def get_business_details(negocio_id):
    try:
        # Busca el negocio en la base de datos por su ID
        negocio = db.negocios.find_one({'_id': ObjectId(negocio_id)})
        if negocio:
            # Si el negocio se encuentra, renderiza la plantilla con los datos
            # Asegúrate de pasar toda la información necesaria
            print (negocio)
            return render_template('negocio.html', negocio=negocio)
        else:
            # Si el negocio no se encuentra, devuelve un error 404
            return "Negocio no encontrado", 404
    except Exception as e:
        return f"Error al procesar la solicitud: {e}", 500


@app.route('/api/register', methods=['POST'])
def register():
    """
    Ruta para registrar a un nuevo usuario.
    """
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validación básica
    if not name or not email or not password:
        return jsonify({"error": "Todos los campos son obligatorios."}), 400

    # Verificar si el usuario ya existe
    if db.usuarios.find_one({'email': email}):
        return jsonify({"error": "Este correo ya está registrado."}), 409

    # Hash de la contraseña para seguridad
    #hashed_password = generate_password_hash(password, method='sha256')

    # Crear el nuevo documento de usuario
    new_user = {
        'nombre': name,
        'email': email,
        'password_hash': password,
        'fecha_registro': datetime.now()
    }

    try:
        # Insertar el nuevo usuario en la colección 'usuarios'
        db.usuarios.insert_one(new_user)
        return jsonify({"message": "Registro exitoso. Ahora puedes iniciar sesión."}), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar el usuario: {str(e)}"}), 500

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/popular_businesses')
def get_popular_businesses():
    """
    Ruta para obtener los 4 negocios más populares (mejor ranking).
    """
    try:
        # Busca los 4 negocios con el mejor promedio de ranking
        popular_businesses = list(db.negocios.find().sort('promedio_ranking', -1).limit(4))

        # Convierte los resultados a un formato serializable
        businesses_json = [
            {
                'id': str(b['_id']),
                'name': b['nombre'],
                'category': b['categoria'],
                'ranking': b.get('promedio_ranking', 0),
                'image_url': b.get('imagen_url', 'https://via.placeholder.com/300x200'),
                'lat': b.get('coordenadas', {}).get('lat'),
                'lng': b.get('coordenadas', {}).get('lon')
            } for b in popular_businesses
        ]
        return jsonify(businesses_json), 200
    except Exception as e:
        print(f"Error al obtener negocios populares: {e}")
        return jsonify({"error": "Ocurrió un error en el servidor."}), 500

if __name__ == '__main__':
    app.run()
