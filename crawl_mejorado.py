import asyncio
import os
import requests
from typing import List
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

# --- CONFIGURACIÓN ---
OUTPUT_DIR = "descargas_pro"

async def obtener_urls_sitemap(url: str) -> List[str]:
    """Lee un archivo XML de sitemap."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [loc.text for loc in root.findall('.//ns:loc', namespace)]
    except Exception as e:
        print(f"❌ Error al leer sitemap: {e}")
        return []

async def descubrir_links_en_pagina(url_base: str) -> List[str]:
    """Entra a una página y extrae todos los enlaces internos relacionados."""
    print(f"🔍 Analizando enlaces en: {url_base}...")
    
    config = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=config) as crawler:
        result = await crawler.arun(url=url_base)
        if not result.success:
            print(f"❌ No se pudo acceder a la página: {result.error_message}")
            return []

        enlaces_internos = []
        dominio_base = urlparse(url_base).netloc
        ruta_base = urlparse(url_base).path

        for link_dict in result.links.get("internal", []):
            href = link_dict.get("href", "")
            full_url = urljoin(url_base, href)
            if dominio_base in full_url and ruta_base in full_url:
                enlaces_internos.append(full_url)
        
        return sorted(list(set(enlaces_internos)))

async def ejecutar_rastreo(urls: List[str]):
    """Lógica central de descarga con LIMPIEZA CORREGIDA."""
    if not urls: return
    
    print(f"\n🚀 Preparando descarga de {len(urls)} páginas con limpieza profunda...")
    
    # 1. Filtro de densidad de texto
    filtro_global = PruningContentFilter(
        threshold=0.6,
        min_word_threshold=50
    )

    # 2. Generador de Markdown
    generador_limpio = DefaultMarkdownGenerator(
        content_filter=filtro_global,
        options={
            "ignore_links": True,
            "ignore_images": True,
            "body_width": 0
        }
    )

    browser_cfg = BrowserConfig(headless=True)
    # Se eliminó 'fit_markdown' de aquí para evitar errores de versión
    crawl_cfg = CrawlerRunConfig(
        markdown_generator=generador_limpio,
        cache_mode=CacheMode.ENABLED,
        exclude_external_links=True,
        exclude_social_media_links=True,
        remove_overlay_elements=True
    )

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        results = await crawler.arun_many(urls=urls, config=crawl_cfg)
        
        exitos = 0
        for i, res in enumerate(results):
            if res.success:
                nombre = urls[i].rstrip("/").split("/")[-1] or f"page_{i}"
                if not nombre or nombre == urlparse(urls[i]).netloc: nombre = f"index_{i}"
                
                # Intentar usar la versión más limpia disponible en el objeto de resultado
                # Algunos versiones de crawl4ai lo ponen en res.markdown.fit_markdown
                # Si no existe, usamos el raw_markdown que ya está filtrado por el PruningContentFilter
                final_content = res.markdown.raw_markdown
                if hasattr(res.markdown, 'fit_markdown') and res.markdown.fit_markdown:
                    final_content = res.markdown.fit_markdown

                ruta_archivo = os.path.join(OUTPUT_DIR, f"{i+1}_{nombre}.md")
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(f"--- FUENTE: {urls[i]} ---\n\n")
                    f.write(final_content)
                exitos += 1
                print(f"✅ [{i+1}] Guardado (Limpio): {nombre}.md")
            else:
                print(f"❌ [{i+1}] Error en {urls[i]}: {res.error_message}")
        
        print(f"\n✨ Proceso finalizado. Archivos en '{os.path.abspath(OUTPUT_DIR)}'")

async def main():
    while True:
        print("\n=== CRAWL4AI: SELECTOR DE ESTRATEGIA (LIMPIEZA ULTRA-PRO) ===")
        url_usuario = input("Introduce la URL (o presiona Enter para salir): ").strip()
        
        if not url_usuario: 
            print("Cerrando el programa...")
            break

        urls = []

        if url_usuario.endswith(".xml"):
            print("📂 Modo: Sitemap XML.")
            urls = await obtener_urls_sitemap(url_usuario)
        else:
            print("🌐 Modo: Página Web.")
            print("   1. Solo esta página (Rápido)")
            print("   2. Smart Crawl (Sección completa)")
            opcion = input("\nElige una opción (1 o 2): ").strip()
            
            if opcion == "2":
                urls = await descubrir_links_en_pagina(url_usuario)
                if url_usuario not in urls: 
                    urls.insert(0, url_usuario)
                print(f"🔗 Se encontraron {len(urls)} URLs relacionadas.")
            else:
                urls = [url_usuario]

        if urls:
            print(f"\nSe procesarán {len(urls)} URLs con inteligencia de filtrado.")
            confirmar = input("¿Confirmas la descarga? (s/n): ").lower()
            if confirmar == 's':
                await ejecutar_rastreo(urls)
            else:
                print("Operación cancelada.")
        else:
            print("No se encontraron URLs válidas.")
        
        opcion_final = input("\n¿Deseas procesar otro link? (s/n): ").lower().strip()
        if opcion_final != 's':
            print("👋 ¡Proceso finalizado! Hasta luego.")
            break

if __name__ == "__main__":
    asyncio.run(main())
