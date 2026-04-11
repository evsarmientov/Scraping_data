#Importando todas las librerías necesarias
import base64
import time
import os

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

#----------------------------------------------------------------------
#Creación de funciones auxiliares:

#Función 1: decodifica los nombres que el sitio oculta en formato base64
#El sitio guarda los nombres como texto cifrado en el atributo data-auth
#para evitar scrapers simples. Esta función los convierte a texto legible.
def decode_obfuscated(data_auth):
    try:
        return base64.b64decode(data_auth).decode("utf-8")
    except Exception:
        return data_auth

#Función 2: lee todas las filas visibles en la página actual de la tabla
#Usa BeautifulSoup para parsear el HTML de forma rápida, recorre cada fila
#y celda, y decodifica los nombres ocultos cuando los encuentra
def extract_page(driver):
    #Obtenemos el HTML completo de la página actual desde Selenium
    soup = BeautifulSoup(driver.page_source, "lxml")
    #Ubicamos el cuerpo de la tabla de postulantes
    tbody = soup.select_one("#tablaPostulantes tbody")
    rows = []
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        row = []
        for td in tds:
            #Verificamos si la celda tiene contenido oculto (nombre cifrado)
            obf = td.find(class_="obfuscated")
            if obf and obf.get("data-auth"):
                #Si está cifrado, lo decodificamos
                row.append(decode_obfuscated(obf["data-auth"]))
            else:
                #Si no está cifrado, lo leemos directamente
                row.append(td.get_text(strip=True))
        if row:
            rows.append(row)
    return rows

#Función 3: extrae todos los postulantes de una carrera recorriendo todas sus páginas
#DataTables solo muestra 50 filas a la vez, por eso navegamos página por página
#usando su propia API de JavaScript para garantizar que no se pierda ningún dato
def scrape_career(driver, url, career_name):
    #Abrimos la página de resultados de la carrera
    driver.get(url)
    #Esperamos hasta que la tabla esté presente en la página
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "tablaPostulantes"))
    )
    time.sleep(1)

    #Preguntamos a DataTables cuántas páginas tiene esta carrera
    total_pages = driver.execute_script(
        "return $('#tablaPostulantes').DataTable().page.info().pages;"
    )

    all_rows = []
    for page_num in range(total_pages):
        if page_num > 0:
            #Guardamos el texto informativo actual ("Mostrando 1 a 50 de X")
            #para detectar cuando la tabla termine de actualizarse
            current_info = driver.find_element(By.ID, "tablaPostulantes_info").text

            #Le indicamos a DataTables que navegue a la página número page_num
            driver.execute_script(
                f"$('#tablaPostulantes').DataTable().page({page_num}).draw('page');"
            )

            #Esperamos hasta que el texto informativo cambie, confirmando
            #que la tabla ya cargó los nuevos datos antes de leerlos
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.ID, "tablaPostulantes_info").text != current_info
            )

        #Leemos las filas de la página actual y las acumulamos
        all_rows.extend(extract_page(driver))

    return all_rows

#----------------------------------------------------------------------
def main():
    #Abriendo el navegador con Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        #Extraer el link de todas las carreras
        INDEX_URL = "https://admision.unmsm.edu.pe/Website20262/A/A.html"

        #Abrimos la página índice con Selenium
        driver.get(INDEX_URL)

        #Esperamos hasta que al menos un link de resultados esté presente en la página
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='results.html']"))
        )

        #Buscamos todos los links que apunten a una página de resultados
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='results.html']")

        #Guardamos una lista de pares (nombre de carrera, url) descartando links vacíos
        careers = [
            (link.text.strip(), link.get_attribute("href"))
            for link in links
            if link.text.strip()
        ]

        print(f"Total de carreras encontradas: {len(careers)}")

        #Scrapear todas las carreras
        COLUMNS = ["Código", "Apellidos y Nombres", "Escuela", "Puntaje", "Mérito E.P", "Observación"]

        all_data = []

        for career_name, url in tqdm(careers, desc="Scrapeando carreras"):
            tqdm.write(f"  → {career_name}")
            try:
                rows = scrape_career(driver, url, career_name)
                all_data.extend(rows)
                tqdm.write(f"     ✓ {len(rows)} postulantes")
            except Exception as e:
                tqdm.write(f"     ERROR: {e}")

        print(f"\nTotal de filas recolectadas: {len(all_data)}")

        #Guardar en Excel
        os.makedirs("output", exist_ok=True)
        OUTPUT_PATH = os.path.join("output", "resultados_sanmarcos.xlsx")

        df = pd.DataFrame(all_data, columns=COLUMNS)
        df.to_excel(OUTPUT_PATH, index=False)

        print(f"Archivo guardado: {OUTPUT_PATH}")
        print(f"Total filas: {len(df)}")

    finally:
        #Cerrar el navegador al terminar
        driver.quit()

if __name__ == "__main__":
    main()
