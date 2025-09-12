from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from model.recommendation_engine import train_model, recommend_for_user 

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

    return render_template('index.html', recommendations=recommendations_for_template, user_id=user_id)

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
            return jsonify({"message": "Inicio de sesión exitoso", "user_id": str(user['_id'])}), 200
        return jsonify({"message": "Credenciales inválidas"}), 401
    return render_template("login.html", titulo= "Login")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home')) # Redirige a la página principal

# --- Endpoint de API para el frontend (si se necesita una llamada asíncrona) ---
@app.route('/api/recomendaciones/<user_id>')
def get_recommendations_api(user_id):
    try:
        if user_id == "popular":
            recommendations = list(db.negocios.find().sort('promedio_ranking', -1).limit(5))
        else:
            user_id_obj = ObjectId(user_id)
            recommendations = recommend_for_user(user_id_obj, item_similarity_df)

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

if __name__ == '__main__':
    app.run(debug=True)
