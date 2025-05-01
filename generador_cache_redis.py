
import random
import time
import json
from pymongo import MongoClient
from redis import Redis
from collections import defaultdict
import numpy as np

# Configuración
MONGO_URI = "mongodb://localhost:27017/"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
DB_NAME = "waze"
COLLECTION_NAME = "eventos"
ITERACIONES = 1500
DISTRIBUCION = "zipf"  # o "uniforme"
USAR_TTL = False  # Cambiar a True para usar TTL por clave
TTL_SEGUNDOS = 60

# Conexión a MongoDB y Redis
mongo_client = MongoClient(MONGO_URI)
mongo_collection = mongo_client[DB_NAME][COLLECTION_NAME]
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Obtener tipos únicos
tipos_eventos = mongo_collection.distinct("tipo")
print(f"🎯 Tipos de evento disponibles: {tipos_eventos}")

# Métricas
hits = 0
misses = 0
frecuencia = defaultdict(int)
duraciones = []

# Generador de tráfico con cache
for i in range(ITERACIONES):
    if DISTRIBUCION == "uniforme":
        tipo = random.choice(tipos_eventos)
    elif DISTRIBUCION == "zipf":
        index = min(np.random.zipf(2), len(tipos_eventos)) - 1
        tipo = tipos_eventos[index]
    else:
        raise ValueError("Distribución no válida.")

    cache_key = f"eventos:{tipo}"
    inicio = time.time()

    if redis_client.exists(cache_key):
        data = json.loads(redis_client.get(cache_key))
        hits += 1
    else:
        data = list(mongo_collection.find({"tipo": tipo}, {"_id": 0}))
        redis_client.set(cache_key, json.dumps(data))
        if USAR_TTL:
            redis_client.expire(cache_key, TTL_SEGUNDOS)
        misses += 1

    duracion = time.time() - inicio
    duraciones.append(duracion)
    frecuencia[tipo] += 1
    print(f"[{i+1}] '{tipo}' - {len(data)} eventos - {'HIT' if cache_key in redis_client else 'MISS'} - {duracion:.4f}s")

# Reporte final
print("\n📊 Resumen:")
print(f" - Consultas totales: {ITERACIONES}")
print(f" - Cache hits: {hits}")
print(f" - Cache misses: {misses}")
print(f" - Hit rate: {(hits / ITERACIONES * 100):.2f}%")
print(f" - Tiempo promedio de respuesta: {sum(duraciones)/len(duraciones):.4f}s")
