import polars as pl
from pathlib import Path

# Configuración
PARQUET_PATH = Path("crawl4ai/descargas_pro/data_productos.parquet")
OUTPUT_MD = Path("crawl4ai/descargas_pro/analisis_ia_productos.md")

def generar_perfil_ia():
    if not PARQUET_PATH.exists():
        print(f"❌ No se encuentra el archivo: {PARQUET_PATH}")
        return

    print(f"📖 Leyendo {PARQUET_PATH.name}...")
    df = pl.read_parquet(PARQUET_PATH)

    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# 🤖 Perfil de Datos para Análisis de IA\n\n")
        
        # 1. Metadatos del Dataset
        f.write("## 📊 Información General\n")
        f.write(f"- **Total de Filas:** {df.height:,}\n")
        f.write(f"- **Total de Columnas:** {df.width}\n")
        f.write(f"- **Peso en Memoria:** {df.estimated_size('mb'):.2f} MB\n\n")

        # 2. Análisis de Calidad (Nulls)
        f.write("## 🔍 Auditoría de Calidad (Valores Nulos)\n")
        f.write("| Columna | No Nulos | % Completado |\n")
        f.write("| :--- | :--- | :--- |\n")
        for col in df.columns:
            non_null = df[col].null_count()
            percent = ((df.height - non_null) / df.height) * 100
            f.write(f"| {col} | {df.height - non_null:,} | {percent:.1f}% |\n")
        f.write("\n")

        # 3. Estadísticas de Precios (Solo columnas numéricas detectadas)
        f.write("## 💰 Resumen de Precios\n")
        numeric_cols = [c for c, t in zip(df.columns, df.dtypes) if t in [pl.Float64, pl.Int64] and "precio" in c.lower()]
        if numeric_cols:
            stats = df.select(numeric_cols).describe()
            # Convertimos a Pandas solo para el to_markdown que es más limpio para IA
            import pandas as pd
            f.write(stats.to_pandas().to_markdown(index=False))
        else:
            f.write("*No se detectaron columnas numéricas de precio para estadísticas directas.*\n")
        f.write("\n\n")

        # 4. Distribución por Marca (Top 20)
        f.write("## 🏷️ Top 20 Marcas por Volumen\n")
        if "productos_marca" in df.columns:
            brand_dist = df["productos_marca"].value_counts().sort("count", descending=True).head(20)
            f.write(brand_dist.to_pandas().to_markdown(index=False))
        f.write("\n\n")

        # 5. Muestra de Datos (Primeros 50)
        f.write("## 📑 Muestra Representativa (Primeros 50 registros)\n")
        # Seleccionamos columnas clave para no saturar el ancho del Markdown
        cols_clave = ["id_producto", "productos_descripcion", "productos_marca", "precio_unitario_bulto_por_unidad_venta_con_iva"]
        # Si las columnas clave no existen, usamos todas
        cols_to_show = [c for c in cols_clave if c in df.columns] or df.columns[:8]
        
        sample = df.select(cols_to_show).head(50)
        f.write(sample.to_pandas().to_markdown(index=False))

    print(f"✅ Informe generado con éxito: {OUTPUT_MD}")

if __name__ == "__main__":
    generar_perfil_ia()
