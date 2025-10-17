import asyncio
import os
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import requests
from xml.etree import ElementTree


async def crawl_sequential(urls: List[str], limite_urls: int = None):
    print("\n=== Sequential Crawling with Session Reuse ===")

    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    output_dir = r"C:\Users\Atencion online 2\Desktop\crawl_descargados"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        session_id = "session1"
        contador = 0
        
        for url in urls:
            # Limitar cantidad de URLs si se especifica
            if limite_urls and contador >= limite_urls:
                print(f"\nLímite de {limite_urls} URLs alcanzado. Deteniendo...")
                break
            
            try:
                print(f"\n[{contador + 1}] Descargando: {url}")
                print("Presiona Ctrl+C para pausar/detener\n")
                
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id=session_id
                )
                
                if result.success:
                    print(f"✓ Éxito: {url}")
                    print(f"  Tamaño: {len(result.markdown.raw_markdown)} caracteres")
                    
                    # Construir nombre de archivo seguro
                    segmento = url.rstrip("/").split("/")[-1] or "index"
                    nombre_archivo = f"{contador + 1}_{segmento}.md"
                    ruta_archivo = os.path.join(output_dir, nombre_archivo)
                    
                    with open(ruta_archivo, "w", encoding="utf-8") as f:
                        f.write(f"# {url}\n\n")
                        f.write(result.markdown.raw_markdown)
                    
                    print(f"  Guardado: {ruta_archivo}")
                    contador += 1
                else:
                    print(f"✗ Falló: {url} - Error: {result.error_message}")
                    
            except KeyboardInterrupt:
                print("\n\n⚠ Descarga pausada por el usuario")
                respuesta = input("¿Deseas continuar? (s/n): ")
                if respuesta.lower() != 's':
                    print(f"Descarga detenida. Se descargaron {contador} archivos.")
                    break
                    
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        await crawler.close()
        print(f"\n✓ Proceso finalizado. Total descargado: {contador} archivos")
        print(f"Guardados en: {output_dir}")


def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap ("https://docs.crawl4ai.com/sitemap.xml") to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://docs.crawl4ai.com/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []


async def main():
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        
        # AQUÍ puedes especificar cuántas URLs descargar
        # Por ejemplo: limite_urls=5 descargará solo 5 URLs
        limite = input("¿Cuántas URLs deseas descargar? (presiona Enter para todas): ")
        
        if limite.strip():
            try:
                limite = int(limite)
                await crawl_sequential(urls, limite_urls=limite)
            except ValueError:
                print("Número inválido, descargando todas...")
                await crawl_sequential(urls)
        else:
            await crawl_sequential(urls)
    else:
        print("No URLs found to crawl")


if __name__ == "__main__":
    asyncio.run(main())