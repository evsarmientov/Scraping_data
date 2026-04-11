# 🕷️ Scraping_data
### Evelyn Valeria Sarmiento Vásquez

Repositorio con dos tareas de extracción y análisis de datos usando Python:
web scraping con Selenium y consumo de una API REST.

---

## 📁 Estructura del repositorio

```
Scraping_data/
│
├── scraper.py                        # Task 1 — Script principal de web scraping
├── README.md                         # Este archivo
│
├── output/
│   └── resultados_sanmarcos.xlsx     # Excel consolidado con todos los resultados
│
├── api/
│   ├── tarea_rawg_api.ipynb          # Task 2 — Notebook de análisis con la API de RAWG
│   └── output/
│       └── top20_rawg.csv            # CSV con el top 20 de juegos de todos los tiempos
│
└── video/
    └── link.txt                      # Link al video explicativo
```

---

## 🎓 Task 1 — Web Scraping UNMSM

### 📌 ¿Qué hace?
Extrae automáticamente los resultados del examen de admisión de la
**Universidad Nacional Mayor de San Marcos (UNMSM) 2026-II**, carrera por carrera,
y consolida toda la información en un único archivo Excel.

### 📦 Instalación de dependencias
```bash
pip install selenium webdriver-manager beautifulsoup4 lxml pandas tqdm openpyxl
```

### ▶️ ¿Cómo ejecutarlo?
```bash
python scraper.py
```
El script abre Chrome automáticamente, recorre todas las carreras y guarda el Excel al terminar.

### ⚙️ ¿Cómo funciona internamente?
1. Selenium abre Chrome y navega a la página índice de admisión
2. Extrae los enlaces de todas las carreras disponibles (~111 carreras)
3. Por cada carrera, navega a su página de resultados
4. Usa la API de DataTables vía JavaScript para detectar cuántas páginas tiene
5. Recorre cada página y lee las filas con BeautifulSoup
6. Decodifica los nombres en base64 que el sitio usa para ofuscar los datos
7. Consolida todo en un único DataFrame y lo exporta a Excel

### 💡 Desafío principal
La tabla usa **DataTables** con paginación de 50 filas por página. Se usó la API
de JavaScript de DataTables para detectar el número total de páginas y navegar
a cada una automáticamente, sin hacer clic manualmente.

### 📊 ¿Qué contiene el output?
- **Archivo:** `output/resultados_sanmarcos.xlsx`
- **Columnas:** Código, Apellidos y Nombres, Escuela, Puntaje, Mérito E.P, Observación

---

## 🎮 Task 2 — API REST: RAWG Video Games Database

### 📌 ¿Qué hace?
Consume la **API de RAWG** para extraer, analizar y comparar datos de
videojuegos: los mejor valorados por Metacritic, comparaciones por plataforma,
género y año, y exporta un ranking de los top 20 juegos de todos los tiempos.

### 📦 Instalación de dependencias
```bash
pip install requests pandas
```

### ▶️ ¿Cómo ejecutarlo?
```bash
# Abrir api/tarea_rawg_api.ipynb en Jupyter y correr las celdas en orden.
# Al llegar a la celda de API Key, ingresar tu key cuando se solicite:
# Ingresa tu RAWG API Key: ········
```
> ⚠️ Necesitas una API Key gratuita de [https://rawg.io/apidocs](https://rawg.io/apidocs)

### 📋 Estructura del análisis

| Parte | Contenido |
|---|---|
| **A** 🟢 | Exploración general — total de juegos registrados en RAWG |
| **B** 🔵 | Análisis por categorías — top Metacritic y mejores juegos en Steam |
| **C** 🟡 | Comparaciones — PC vs PS5, saga Zelda, géneros, años y exportar CSV |
| **D** 🔴 | Insights y conclusiones personales |

### 💡 Hallazgos principales
- 🏆 RAWG tiene registrados más de **898,000 juegos**
- 🧓 Los juegos clásicos dominan el Metacritic — Ocarina of Time (1998) supera a entregas modernas de la misma saga
- 🖥️ PC tiene mejor Metacritic promedio que PS5, posiblemente por su mayor accesibilidad
- 🗺️ El género **Adventure** tiene el rating promedio más alto entre los géneros más populares
- 📅 El año **2018** tuvo los juegos con mayor Metacritic promedio vs 2020 y 2023

### 📊 ¿Qué contiene el output?
- **Archivo:** `api/output/top20_rawg.csv`
- **Columnas:** name, rating, metacritic, release_date, main_genre