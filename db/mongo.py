import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

load_dotenv()

# --- Conexión a MongoDB ---
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("No se ha definido la variable de entorno MONGO_URI.")
    
client = MongoClient(mongo_uri) 
db = client[os.getenv('MONGO_DB_NAME')] # El nombre de la base de datos también se lee desde .env

# --- Obtiene los datos para el chat Bot ---
def get_corpus():
    return list(db.corpus.find())