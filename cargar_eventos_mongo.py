
import json
from pymongo import MongoClient

# Conexión a MongoDB (nombre del servicio en docker-compose)
client = MongoClient("mongodb://localhost:27017/")
db = client["waze"]
collection = db["eventos"]

# Cargar eventos desde el archivo JSON acumulado
with open("eventos_acumulados.json", "r", encoding="utf-8") as f:
    eventos = json.load(f)

# Insertar en MongoDB
result = collection.insert_many(eventos)
print(f"✅ Insertados {len(result.inserted_ids)} eventos en MongoDB.")
