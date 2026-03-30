import os
import sys
import csv
from pathlib import Path
from typing import Optional

# --- MOTOR DE CHEQUEO DE DEPENDENCIAS ---
def verify_environment():
    """Verifica el entorno y prepara fallbacks para dependencias faltantes."""
    status = {"polars": False, "reporting": False}
    
    try:
        import polars as pl
        status["polars"] = True
    except ImportError:
        print("❌ ERROR CRÍTICO: La librería 'polars' no está instalada.")
        print("💡 Ejecuta: pip install polars")
        sys.exit(1)

    try:
        import pandas
        import pyarrow
        import tabulate
        status["reporting"] = True
    except ImportError:
        print("\n⚠️  MODO COMPATIBILIDAD ACTIVADO")
        print("   Faltan: pyarrow, pandas o tabulate.")
        print("   El resumen Markdown será básico (formato texto).\n")
        print("💡 Para mejorar los reportes: pip install pyarrow pandas tabulate\n")
    
    return status

# Inicializar entorno
ENV_STATUS = verify_environment()
import polars as pl

# --- CONFIGURACIÓN ---
DEFAULT_OUTPUT = Path("descargas_pro")

class CSVProcessor:
    def __init__(self, output_dir: Path = DEFAULT_OUTPUT):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_separator(self, file_path: Path) -> str:
        """Detecta el separador usando Sniffer de CSV con fallback manual."""
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(4096) # Leemos un bloque pequeño
                if not sample: return ','
                
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;||\t')
                    return dialect.delimiter
                except Exception:
                    # Fallback manual basado en frecuencia
                    separators = ['|', ';', ',', '\t']
                    return max(separators, key=lambda s: sample.count(s))
        except Exception:
            return ','

    def generate_report(self, df: pl.DataFrame, file_path: Path, sep: str, parquet_path: Path):
        """Genera un reporte Markdown con fallback a texto plano si falta pyarrow/pandas."""
        nombre_base = file_path.stem.replace(" ", "_")
        report_path = self.output_dir / f"resumen_{nombre_base}.md"
        
        try:
            with report_path.open("w", encoding="utf-8") as f:
                f.write(f"# Resumen de Datos: {file_path.name}\n\n")
                f.write(f"--- ORIGEN: `{file_path}` ---\n\n")
                f.write("## 📊 Estadísticas\n")
                f.write(f"- **Registros:** {df.height:,}\n")
                f.write(f"- **Columnas:** {df.width}\n")
                f.write(f"- **Separador:** `{sep}`\n")
                f.write(f"- **Formato Optimizado:** `{parquet_path.name}`\n\n")
                
                f.write("## 📝 Esquema de Datos\n")
                for col in df.columns:
                    f.write(f"- {col}\n")
                
                f.write("\n## 🔍 Vista Previa (Top 10)\n")
                
                if ENV_STATUS["reporting"]:
                    try:
                        # Formato Pro con Tabulate
                        import pandas as pd
                        f.write(df.head(10).to_pandas().to_markdown(index=False))
                    except Exception:
                        f.write(f"```text\n{df.head(10)}\n```")
                else:
                    # Formato texto plano (nativo de Polars)
                    f.write("```text\n")
                    f.write(str(df.head(10)))
                    f.write("\n```\n")
                    f.write("\n> *Nota: Instale 'pyarrow' y 'tabulate' para una mejor visualización aquí.*")
                    
            return report_path
        except Exception as e:
            print(f"⚠️ No se pudo generar el reporte: {e}")
            return None

    def process_file(self, ruta_str: str):
        path = Path(ruta_str.replace('"', '').replace("'", ""))
        
        if not path.is_file():
            print(f"❌ Error: El archivo '{path}' no existe.")
            return

        print(f"\n🚀 ANALIZANDO: {path.name}")
        print("-" * 30)

        try:
            sep = self.detect_separator(path)
            print(f"🔍 Separador: '{sep}' | Motor: Polars (Rust)")

            # Lectura optimizada
            df = pl.read_csv(
                path,
                separator=sep,
                ignore_errors=True,
                infer_schema_length=10000,
                truncate_ragged_lines=True,
                encoding='utf-8-lossy'
            )

            # Guardado en Parquet
            nombre_base = path.stem.replace(" ", "_")
            parquet_path = self.output_dir / f"data_{nombre_base}.parquet"
            df.write_parquet(parquet_path)
            
            # Reporte
            report_path = self.generate_report(df, path, sep, parquet_path)

            print(f"✅ PROCESO EXITOSO")
            print(f"📂 Datos: {parquet_path.name}")
            if report_path: print(f"📄 Informe: {report_path.name}")
            print(f"📈 Filas: {df.height:,}")

        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {e}")

def main():
    processor = CSVProcessor()
    
    while True:
        print("\n" + "="*45)
        print("       CSV FAST PARSER PRO v2.0")
        print("="*45)
        print("Arrastra el CSV aquí o escribe la ruta.")
        
        entrada = input("\n📥 Ruta del CSV (Enter para salir): ").strip()
        if not entrada: break

        processor.process_file(entrada)

        if input("\n¿Deseas procesar otro archivo? (s/n): ").lower().strip() != 's':
            break

    print("\n👋 ¡Proceso finalizado!")

if __name__ == "__main__":
    main()
