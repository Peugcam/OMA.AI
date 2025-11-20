"""
Script para verificar o dashboard usando Playwright
"""
import asyncio
from playwright.async_api import async_playwright

async def check_dashboard():
    async with async_playwright() as p:
        # Abrir navegador
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Acessar dashboard
            await page.goto('http://localhost:7860', timeout=10000)

            # Aguardar carregamento
            await page.wait_for_timeout(2000)

            # Capturar título
            title = await page.title()
            print(f"Titulo da pagina: {title}")

            # Verificar tabs
            print("\n" + "="*60)
            print("VERIFICACAO DE COMPONENTES:")
            print("="*60)

            # Verificar tab "Gerar Video"
            gerar_video_tab = await page.locator('text=Gerar Video').count()
            print(f"Tab 'Gerar Video' encontrada: {'SIM' if gerar_video_tab > 0 else 'NAO'}")

            # Verificar botao de geracao
            generate_btn = await page.locator('text=Gerar Video OMA App').count()
            print(f"Botao 'Gerar Video OMA App' encontrado: {'SIM' if generate_btn > 0 else 'NAO'}")

            # Verificar outras tabs
            videos_tab = await page.locator('text=Videos').count()
            metadata_tab = await page.locator('text=Metadata').count()
            stats_tab = await page.locator('text=Estatisticas').count()
            print(f"Tab 'Videos' encontrada: {'SIM' if videos_tab > 0 else 'NAO'}")
            print(f"Tab 'Metadata' encontrada: {'SIM' if metadata_tab > 0 else 'NAO'}")
            print(f"Tab 'Estatisticas' encontrada: {'SIM' if stats_tab > 0 else 'NAO'}")

            # Capturar conteúdo principal
            body_text = await page.locator('body').inner_text()

            print("\n" + "="*60)
            print("CONTEUDO DO DASHBOARD:")
            print("="*60)
            print(body_text[:1000])  # Primeiros 1000 caracteres
            print("="*60)

            # Tirar screenshot
            await page.screenshot(path='dashboard_screenshot.png')
            print("\nScreenshot salvo: dashboard_screenshot.png")

        except Exception as e:
            print(f"Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_dashboard())
