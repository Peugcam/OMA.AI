"""
Test Video Generation - Simula o fluxo completo
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

async def test_generate_video():
    print("🎬 Testando Geração de Vídeo...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False para ver o processo
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            print("\n🌐 Abrindo dashboard...")
            await page.goto("http://localhost:7861", timeout=30000)
            await page.wait_for_load_state("networkidle")

            print("✅ Dashboard carregado!")

            # Aguardar o Gradio carregar completamente
            await asyncio.sleep(3)

            print("\n📋 Selecionando template 'Produto Tech'...")

            # Procurar o dropdown de templates
            template_dropdown = await page.query_selector("select, .dropdown")
            if template_dropdown:
                # Clicar no dropdown
                await template_dropdown.click()
                await asyncio.sleep(1)

                # Tentar selecionar "Produto Tech"
                await page.keyboard.press("ArrowDown")
                await asyncio.sleep(0.5)
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)

                print("✅ Template selecionado!")

                # Screenshot após selecionar template
                await page.screenshot(path="step1_template_selected.png")
                print("📸 Screenshot: step1_template_selected.png")

            print("\n🎯 Verificando campos preenchidos...")
            await asyncio.sleep(2)

            # Screenshot dos campos preenchidos
            await page.screenshot(path="step2_fields_filled.png")
            print("📸 Screenshot: step2_fields_filled.png")

            print("\n🚀 Procurando botão 'Gerar Vídeo'...")

            # Procurar botão de gerar
            generate_buttons = await page.query_selector_all("button")

            for btn in generate_buttons:
                text = await btn.inner_text()
                if "Gerar Vídeo" in text or "Gerar" in text:
                    print(f"✅ Botão encontrado: '{text}'")

                    # Scroll até o botão
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1)

                    # Screenshot antes de clicar
                    await page.screenshot(path="step3_before_generate.png")
                    print("📸 Screenshot: step3_before_generate.png")

                    print("\n🎬 Clicando em 'Gerar Vídeo'...")
                    await btn.click()

                    print("⏳ Aguardando geração (simulação demo - 10 segundos)...")

                    # Aguardar processo
                    for i in range(10):
                        await asyncio.sleep(1)
                        print(f"   {i+1}/10 segundos...")

                    # Screenshot durante geração
                    await page.screenshot(path="step4_generating.png", full_page=True)
                    print("📸 Screenshot: step4_generating.png")

                    # Aguardar mais um pouco
                    await asyncio.sleep(5)

                    # Screenshot final
                    await page.screenshot(path="step5_result.png", full_page=True)
                    print("📸 Screenshot: step5_result.png")

                    # Pegar texto da página para ver resultado
                    page_text = await page.evaluate("document.body.innerText")

                    if "SUCESSO" in page_text or "DEMO" in page_text:
                        print("\n✅ GERAÇÃO CONCLUÍDA!")
                        if "DEMO" in page_text:
                            print("   (Modo Demo - quick_generate.py não encontrado)")
                        else:
                            print("   (Vídeo real gerado!)")
                    else:
                        print("\n⚠️ Verifique o status na interface")

                    break

            print("\n🎉 Teste completo!")
            print("\n📸 Screenshots gerados:")
            print("   1. step1_template_selected.png")
            print("   2. step2_fields_filled.png")
            print("   3. step3_before_generate.png")
            print("   4. step4_generating.png")
            print("   5. step5_result.png")

            # Manter navegador aberto por 10 segundos para você ver
            print("\n⏸️ Mantendo navegador aberto por 10 segundos...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n❌ Erro: {e}")
            await page.screenshot(path="error_generation.png")
            print("📸 Error screenshot: error_generation.png")

        finally:
            await browser.close()
            print("\n✅ Teste finalizado!")

if __name__ == "__main__":
    asyncio.run(test_generate_video())
