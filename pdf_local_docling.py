import os
import sys

# Intentamos importar las librerías necesarias
try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("❌ Error: No se encontró la librería 'docling'.")
    print("💡 Instálala con: pip install docling")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("❌ Error: No se encontró 'pandas'.")
    print("💡 Instálala con: pip install pandas")
    sys.exit(1)

# --- CONFIGURACIÓN ---
OUTPUT_DIR = "descargas_pro"
FORMATOS_SOPORTADOS = [".pdf", ".docx", ".xlsx", ".pptx", ".html", ".md", ".csv"]

def procesar_archivo_local(ruta_archivo):
    """Convierte un documento a Markdown localmente con soporte robusto para CSV."""
    nombre_archivo = os.path.basename(ruta_archivo)
    extension = os.path.splitext(nombre_archivo)[1].lower()
    
    print(f"\n⚙️  Analizando documento ({extension}): {nombre_archivo}...")
    
    try:
        if extension == ".csv":
            print("⏳ Procesando tabla CSV (Autodetectando formato)...")
            # Lógica robusta para CSV: detecta separadores y maneja errores de codificación
            try:
                df = pd.read_csv(
                    ruta_archivo, 
                    sep=None, 
                    engine='python', 
                    on_bad_lines='skip', 
                    encoding='utf-8'
                )
            except UnicodeDecodeError:
                # Si falla utf-8, intentamos con latin-1 (común en Windows)
                df = pd.read_csv(
                    ruta_archivo, 
                    sep=None, 
                    engine='python', 
                    on_bad_lines='skip', 
                    encoding='latin-1'
                )
            
            markdown_content = df.to_markdown(index=False)
        else:
            print("⏳ Procesando estructura con Docling...")
            converter = DocumentConverter()
            result = converter.convert(ruta_archivo)
            markdown_content = result.document.export_to_markdown()

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        nombre_limpio = nombre_archivo.replace(extension, "").replace(" ", "_")
        ruta_salida = os.path.join(OUTPUT_DIR, f"local_{nombre_limpio}.md")
        
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(f"--- FUENTE LOCAL: {ruta_archivo} ---\n\n")
            f.write(markdown_content)
        
        print(f"✅ ¡Éxito! Procesado y guardado en: {ruta_salida}")

    except Exception as e:
        print(f"❌ Error crítico al procesar {nombre_archivo}: {e}")

def main():
    while True:
        print("\n=== CONVERTIDOR ROBUSTO (DOCLING + SMART CSV) ===")
        print("Soporta: PDF, Word, Excel, PowerPoint, CSV (Autodetect), HTML")
        ruta = input("Ruta del archivo (o Enter para salir): ").strip()
        
        ruta = ruta.replace('"', '').replace("'", "")

        if not ruta:
            break

        if os.path.isfile(ruta):
            ext = os.path.splitext(ruta)[1].lower()
            if ext in FORMATOS_SOPORTADOS:
                procesar_archivo_local(ruta)
            else:
                print(f"⚠️ El formato '{ext}' no está soportado.")
        else:
            print("⚠️ El archivo no existe.")

        if input("\n¿Procesar otro archivo? (s/n): ").lower().strip() != 's':
            print("👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
