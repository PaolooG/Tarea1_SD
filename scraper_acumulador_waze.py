from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os

ZONAS = [
    {"x_offset": 0, "y_offset": 0},
    {"x_offset": 200, "y_offset": 0},
    {"x_offset": -200, "y_offset": 0},
    {"x_offset": 0, "y_offset": 200},
    {"x_offset": 0, "y_offset": -200},
    {"x_offset": 150, "y_offset": 150},
    {"x_offset": -150, "y_offset": -150},
]

NOMBRE_ARCHIVO = "eventos_acumulados.json"

def iniciar_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.waze.com/es-419/live-map/")
    return driver

def presionar_entendido(driver):
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Entendido')]")
        btn.click()
        print("✔️ Botón 'Entendido' presionado.")
        time.sleep(1)
    except:
        pass

def mover_mapa(driver, acciones, x_offset, y_offset):
    try:
        mapa = driver.find_element(By.CLASS_NAME, "leaflet-map-pane")
        acciones.drag_and_drop_by_offset(mapa, x_offset, y_offset).perform()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Error moviendo el mapa: {e}")
        return False

def extraer_eventos(driver, acciones):
    eventos = []
    iconos = driver.find_elements(By.CLASS_NAME, "leaflet-marker-icon")
    print(f"🔍 Se encontraron {len(iconos)} íconos en esta zona.")
    for i in range(len(iconos)):
        try:
            iconos_actualizados = driver.find_elements(By.CLASS_NAME, "leaflet-marker-icon")
            if i >= len(iconos_actualizados):
                continue
            acciones.move_to_element(iconos_actualizados[i]).click().perform()
            time.sleep(2)
            popup = driver.find_element(By.CLASS_NAME, "leaflet-popup")
            texto = popup.text.strip().split("\n")
            tipo = texto[0] if len(texto) > 0 else "Tipo desconocido"
            ubicacion = texto[1] if len(texto) > 1 else "Ubicación desconocida"
            eventos.append({"tipo": tipo, "ubicacion": ubicacion})
            print(f"  [{i+1}] {tipo} - {ubicacion}")
            driver.find_element(By.CLASS_NAME, "leaflet-popup-close-button").click()
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i+1}] Evento ignorado: {e}")
            continue
    return eventos

def cargar_eventos_previos(nombre_archivo):
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_eventos_acumulados(eventos_nuevos, nombre_archivo):
    eventos_previos = cargar_eventos_previos(nombre_archivo)
    todos = eventos_previos + eventos_nuevos
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=4)
    print(f"✅ Total acumulado: {len(todos)} eventos.")

def main():
    driver = iniciar_driver()
    acciones = ActionChains(driver)
    presionar_entendido(driver)

    time.sleep(8)
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(3):
        body.send_keys(Keys.CONTROL, Keys.SUBTRACT)
        time.sleep(1)

    eventos_totales = []
    for zona in ZONAS:
        print(f"🌍 Moviendo a zona offset x={zona['x_offset']}, y={zona['y_offset']}")
        exito = mover_mapa(driver, acciones, zona["x_offset"], zona["y_offset"])
        if not exito:
            continue
        time.sleep(2)
        eventos = extraer_eventos(driver, acciones)
        eventos_totales.extend(eventos)

    driver.quit()
    guardar_eventos_acumulados(eventos_totales, NOMBRE_ARCHIVO)

if __name__ == "__main__":
    main()
