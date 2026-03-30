import os
import sys
from pathlib import Path
import polars as pl

# --- CONFIGURACIÓN ---
BASE_DIR = Path(r"C:\Users\Atencion online 2\Desktop\Sepa\Sepa_Lunes\2026-03-30")
SEPARATOR = "|"
ENCODING = "utf-8-lossy"

def procesar_carpeta_sepa(folder: Path):
    """Convierte cada CSV de la carpeta en un archivo Parquet individual."""
    print(f"\n📂 Procesando carpeta: {folder.name}")
    
    csv_files = list(folder.glob("*.csv"))
    
    if not csv_files:
        print("   ℹ️ No se encontraron archivos CSV.")
        return

    for csv_path in csv_files:
        parquet_path = csv_path.with_suffix(".parquet")
        print(f"   📄 Convirtiendo: {csv_path.name} -> {parquet_path.name}")
        
        try:
            # Lectura robusta (ignora errores de línea y maneja columnas malformadas)
            df = pl.read_csv(
                csv_path, 
                separator=SEPARATOR, 
                encoding=ENCODING, 
                ignore_errors=True, 
                infer_schema_length=10000, 
                truncate_ragged_lines=True
            )

            # Limpiar espacios en blanco en nombres de columnas
            df = df.rename({c: c.strip() for c in df.columns})

            # Guardar como Parquet
            df.write_parquet(parquet_path)
            print(f"      ✅ OK ({df.height:,} registros)")

        except Exception as e:
            print(f"      ❌ Error al procesar {csv_path.name}: {e}")

def main():
    if not BASE_DIR.exists():
        print(f"❌ Error: No existe la ruta {BASE_DIR}")
        return

    print("="*55)
    print("      SEPA 1-to-1 PARQUET CONVERTER (Polars)")
    print("="*55)
    
    subcarpetas = [d for d in BASE_DIR.iterdir() if d.is_dir()]
    
    if not subcarpetas:
        print("ℹ️ No se encontraron subcarpetas.")
        return

    for folder in subcarpetas:
        procesar_carpeta_sepa(folder)

    print("\n✨ ¡Conversión finalizada!")

if __name__ == "__main__":
    main()
