# 🛒 Proyecto Monitor de Precios (Crawl4AI + SEPA)

Este proyecto automatiza la ingesta y el procesamiento de datos del **SEPA** (Sistema Electrónico de Publicidad de Precios Argentinos) para realizar análisis comparativos de precios en Corrientes Capital.

## 🚀 Instalación y Entorno

Se recomienda usar un entorno virtual (`venv`):

```powershell
python -m venv venv
.\venv\Scripts\activate
```

---

## 🛠️ Scripts del Proyecto

### 1. `csv_parser.py` (Procesador Maestro)
Convierte archivos CSV masivos del SEPA a formato optimizado Parquet con detección automática de separadores.

### 2. `export_for_ai.py` (Perfilador de Datos)
Genera un análisis estadístico y una muestra representativa en Markdown para ser analizada por una IA.

### 3. `crawl_mejorado.py`
Crawler avanzado para extracción de datos web con manejo de sesiones y reintentos. Ideal para descargar paquetes SEPA de forma masiva.

### 4. `crawl_single_page.py`
Script simplificado para la extracción rápida de contenido de una única URL específica.

### 5. `pdf_local_docling.py`
Procesador de archivos PDF (Anexos SEPA) que utiliza el motor **Docling** para convertir documentos complejos a Markdown estructurado.

---

## 📦 Librerías Necesarias

Para que todos los scripts funcionen, instale el siguiente conjunto de dependencias:

- **Procesamiento de Datos:** `polars`, `pyarrow`, `pandas`, `tabulate`
- **Crawling y Web:** `requests`, `crawl4ai`, `beautifulsoup4`
- **Procesamiento PDF:** `docling`, `docling-core`
- **Utilidades:** `pathlib`

---

## 📂 Estructura de Salida (Ignorada en Git)

- `descargas_pro/`: Archivos `.parquet` y reportes `.md`.
- `venv/`: Entorno virtual.
