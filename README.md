# 🏝️ PLATAFORMA DE INTELIGENCIA ARTIFICIAL PARA EL IMPULSO DEL TURISMO EN EL CARMEN DE BOLÍVAR

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Completed-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/Bootcamp-2025-orange.svg" alt="Bootcamp 2025">
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
</p>

Plataforma web basada en Inteligencia Artificial que recomienda negocios, sitios turísticos y experiencias locales en El Carmen de Bolívar, Colombia. Utiliza Machine Learning para sugerir lugares según intereses del usuario, puntuaciones de visitantes y categorías como restaurantes, hospedajes, bares, sitios nocturnos y más.

---
© Raul Ibañez M. 2025
## 🚀 Características principales

- 🔍 Buscador inteligente con motor de recomendaciones
- 🧠 Algoritmo ML basado en similitud de contenido y ranking
- 🗺️ Mapa interactivo con ubicación geográfica de negocios
- 🛠️ Login para ingreso de usuarios y Regisro de usuarios nuevos
- 📱 Diseño responsive para PC, tablet y móviles
- 🔐 Conexión segura con MongoDB Atlas

---

## 🧰 Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, Jinja2
- **Base de datos**: MongoDB Atlas
- **Machine Learning**: Scikit-learn, Pandas
- **Despliegue**: Render.com
- **Mapa**: Leaflet.js + OpenStreetMap

---

## ⚙️ Instalación local (modo desarrollador)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/turismo-el-carmen.git
   cd turismo-el-carmen
   ```
2. Crea un entorno virtual:
   ```bash
	python -m venv venv
	source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Crea un archivo  con tu URI de MongoDB Atlas:
   ```bash
   MONGO_URI=mongodb+srv://usuario:contraseña@cluster0.mongodb.net/turismo?retryWrites=true&w=majority
   ```
5. Ejecuta la app:
   ```bash
   python app.py
   ```
   
## 📦 Estructura del proyecto
```
turismo-el-carmen/
├── db/
│   ├── mongo.py
│   └── seed_db.py
├── model/
│   └── recommendation_engine.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── login.js
│   │   └── register.js
│   └── img/
│       ├── logo.png
│       ├── hero-background.png
│       └── db_img/
│           ├── 1.png
│           ├── 2.png
│           ├── 3.png
│           ├── 4.png
│           └── 5.png
├── templates/
│   ├── index.html
│   ├── register.html
│   └── login.html
├── app.py
├── README.md
└── requirements.txt
```
---

## 🤝 Autor

**Raul Ibáñez M.**

*Freelancer Developer & Technical Lead*

📅 **2025**
