import asyncio
import os

from crawl4ai import AsyncWebCrawler, BrowserConfig

async def main():
    output_dir = "descargas_pro"
    if not os.path.exists(output_dir): os.makedirs(output_dir)


    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://developers.llamaindex.ai/liteparse/guides/multi-format/",
        )
        
        if result.success:
                ruta_archivo = os.path.join(output_dir, "single_page.md")
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                print(f"✅ Guardado con éxito en: {ruta_archivo}")
        else:
                print(f"❌ Error: {result.error_message}")

        
if __name__ == "__main__":
    asyncio.run(main())