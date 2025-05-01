# Tarea1_SD
Este proyecto forma parte de la Tarea 1 del curso de Sistemas Distribuidos. El objetivo es construir una arquitectura modular distribuida que permita obtener, almacenar y consultar eventos de tráfico en la Región Metropolitana de Santiago, utilizando datos desde el mapa en vivo de Waze.

Requisitos:
Python 3.8+
Docker y Docker Compose
Google Chrome instalado
chromedriver compatible con tu versión de Chrome

1) Librerias Python
pip install selenium pymongo redis numpy
2) Configuracion de servicios
docker-compose up -d
Esto inicia:
mongo: Base de datos NoSQL para persistir eventos.
redis: Sistema de caché con política de reemplazo LRU, configurado a 100MB.
3)Extraccion de datos (Scraping)
Ejecuta el scraper para extraer eventos desde el mapa en vivo de Waze:
python scraper_acumulador_waze.py
El script recorre varias zonas del mapa simulando interacciones humanas con Selenium y guarda los eventos en eventos_acumulados.json. OJO: cuando se abra la pestaña chrome apretar el icono entendido. En la consola habra eventos que no captara.
4) Almacenamiento en MongoDB
Una vez extraídos los eventos, se insertan en la base de datos ejecutando:
python cargar_eventos_mongo.py
Esto inserta los eventos en la base waze, colección eventos.
5) Generador de Tráfico + Caché
Este módulo simula 1500 consultas a eventos usando Redis como sistema de caché. Puedes cambiar la distribución de tráfico entre "uniforme" o "zipf".
python generador_cache_redis.py

El script mide:
Tasa de aciertos (cache hit rate)
Tiempos de respuesta
Freuencia de eventos consultados


