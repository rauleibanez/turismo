import pickle
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier

# Cargar el modelo, el vectorizador y el corpus desde el archivo model.pkl
# El corpus cargado tendrá la nueva estructura con la clave 'responses'
try:
    with open("model/model.pkl", "rb") as f:
        model, vectorizer, corpus = pickle.load(f)
except FileNotFoundError:
    print("Error: El archivo 'model/model.pkl' no se encontró. Por favor, entrene el modelo primero.")
    # Considera una solución más robusta para producción
    model = None
    vectorizer = None
    corpus = []

def predict_tag_and_response(text):
    if model is None:
        return "error", "Lo siento, el modelo del asistente no está disponible."
        
    # Vectorizar el texto del usuario
    X_vec = vectorizer.transform([text.lower()])
    
    # Predecir la etiqueta
    tag = model.predict(X_vec)[0]

    # Encontrar la respuesta estática en el corpus para el tag predicho
    for intent in corpus:
        if intent["tag"] == tag:
            # Si el tag es de un negocio, devolvemos solo el tag.
            if "responses" not in intent:
                return tag, None
            # Si tiene respuestas, devolvemos una aleatoria
            return tag, random.choice(intent["responses"])

    # Si no se encuentra un tag válido (o por si acaso)
    return "desconocido", "Lo siento, no entendí tu pregunta. ¿Puedes reformularla?"