import pandas as pd
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("No se ha definido la variable de entorno MONGO_URI.")
    
client = MongoClient(mongo_uri) 
db = client[os.getenv('MONGO_DB_NAME')] # El nombre de la base de datos también se lee desde .env

# Conexión a la base de datos MongoDB
#client = MongoClient('mongodb://localhost:27017/') # Cambia esta URL si tu MongoDB no está en local
#db = client['el_carmen_tourism'] # Nombre de tu base de datos

def train_model():
    """
    Carga los datos de valoraciones de la base de datos y calcula la matriz de similitud.
    """
    # Cargar datos de valoraciones
    ratings_data = list(db.valoraciones.find({}, {'_id': 0}))

    if not ratings_data:
        print("No hay datos de valoraciones para entrenar el modelo.")
        return None, None

    ratings_df = pd.DataFrame(ratings_data)

    # Crear la matriz de usuario-ítem (pivote)
    user_item_matrix = ratings_df.pivot_table(index='usuario_id', columns='negocio_id', values='puntuacion')

    # Rellenar los valores nulos con 0 para el cálculo de similitud
    user_item_matrix.fillna(0, inplace=True)

    # Calcular la similitud del coseno entre negocios
    item_similarity_matrix = cosine_similarity(user_item_matrix.T)
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=user_item_matrix.columns, columns=user_item_matrix.columns)

    return item_similarity_df

def recommend_for_user(user_id, item_similarity_df, num_recommendations=5):
    """
    Genera recomendaciones para un usuario específico.
    """
    # Obtener las valoraciones del usuario
    user_ratings = list(db.valoraciones.find({'usuario_id': user_id}))
    if not user_ratings:
        print(f"Usuario {user_id} no tiene valoraciones.")
        # Devuelve los 5 negocios con mayor rating general
        top_rated_businesses = list(db.negocios.find().sort('promedio_ranking', -1).limit(num_recommendations))
        return top_rated_businesses

    rated_items = [r['negocio_id'] for r in user_ratings]

    # Crear un diccionario para almacenar las recomendaciones
    recommendations = {}

    for item_id in rated_items:
        if item_id in item_similarity_df.columns:
            # Obtener los negocios más similares
            similar_items = item_similarity_df[item_id].sort_values(ascending=False).index[1:] # Excluir el mismo ítem

            for similar_item in similar_items:
                if similar_item not in rated_items:
                    # Sumar las puntuaciones de similitud para cada negocio no valorado
                    if similar_item not in recommendations:
                        recommendations[similar_item] = 0
                    recommendations[similar_item] += item_similarity_df[item_id][similar_item]

    # Ordenar las recomendaciones por puntuación
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

    # Obtener los datos de los negocios recomendados
    recommended_business_ids = [rec[0] for rec in sorted_recommendations[:num_recommendations]]
    recommended_businesses = list(db.negocios.find({'_id': {'$in': recommended_business_ids}}))

    # Si no hay recomendaciones, devuelve los negocios con mayor rating
    if not recommended_businesses:
        top_rated_businesses = list(db.negocios.find().sort('promedio_ranking', -1).limit(num_recommendations))
        return top_rated_businesses

    return recommended_businesses

# Entrenar el modelo al iniciar el servidor
item_similarity_matrix = train_model()
