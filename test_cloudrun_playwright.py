"""
🧪 Teste Automatizado do OMA Video Generator no Cloud Run
=========================================================

Usa Playwright para testar a aplicação em produção.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime


async def test_oma_cloudrun():
    """Testa o dashboard OMA no Cloud Run"""

    # URL do Cloud Run
    url = "https://oma-video-generator-778600940048.southamerica-east1.run.app"

    print(f"\n{'='*70}")
    print(f"🧪 Testando OMA Video Generator no Cloud Run")
    print(f"{'='*70}")
    print(f"🌐 URL: {url}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    async with async_playwright() as p:
        # Lançar navegador
        print("🚀 Lançando navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # Step 1: Acessar a página
            print("\n📄 Step 1: Acessando página...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Tirar screenshot inicial
            await page.screenshot(path="test_results/01_homepage.png")
            print("   ✅ Página carregada - Screenshot salvo")

            # Step 2: Verificar se está em modo demo ou produção
            print("\n🔍 Step 2: Verificando modo de operação...")
            page_content = await page.content()

            if "Modo Demo Ativo" in page_content or "modo demo" in page_content.lower():
                print("   ⚠️  MODO DEMO DETECTADO!")
                print("   ❌ quick_generate.py ainda não foi carregado no container")
                is_demo = True
            else:
                print("   ✅ Modo PRODUÇÃO ativo!")
                is_demo = False

            # Step 3: Preencher formulário
            print("\n📝 Step 3: Preenchendo formulário de geração...")

            # Título
            title_input = page.locator('label:has-text("Título do Vídeo") + * input')
            await title_input.fill("Teste Automatizado Playwright")
            print("   ✅ Título preenchido")

            # Descrição
            desc_textarea = page.locator('label:has-text("Descrição") + * textarea')
            await desc_textarea.fill("Vídeo de teste criado automaticamente via Playwright para validar deploy no Cloud Run.")
            print("   ✅ Descrição preenchida")

            # Duração (slider)
            duration_slider = page.locator('label:has-text("Duração") + * input[type="range"]')
            await duration_slider.fill("30")
            print("   ✅ Duração configurada: 30s")

            # Público-alvo
            audience_input = page.locator('label:has-text("Público-Alvo") + * input')
            await audience_input.fill("Desenvolvedores e QA Engineers")
            print("   ✅ Público-alvo preenchido")

            # Screenshot do form preenchido
            await page.screenshot(path="test_results/02_form_filled.png")
            print("   ✅ Screenshot do formulário salvo")

            # Step 4: Clicar no botão gerar
            print("\n🎬 Step 4: Iniciando geração de vídeo...")
            generate_button = page.locator('button:has-text("Gerar Vídeo")')
            await generate_button.click()
            print("   ✅ Botão 'Gerar Vídeo' clicado")

            # Aguardar progresso (modo demo: ~6s, real: 30-120s)
            wait_time = 10000 if is_demo else 120000
            print(f"   ⏳ Aguardando geração ({wait_time/1000}s max)...")

            # Esperar pela mensagem de sucesso
            try:
                success_msg = page.locator('text=SUCESSO')
                await success_msg.wait_for(timeout=wait_time)
                print("   ✅ Geração concluída!")
            except Exception as e:
                print(f"   ⚠️  Timeout aguardando conclusão: {e}")

            # Screenshot final
            await page.screenshot(path="test_results/03_generation_complete.png", full_page=True)
            print("   ✅ Screenshot final salvo")

            # Step 5: Verificar resultado
            print("\n📊 Step 5: Verificando resultado...")
            final_content = await page.content()

            if "MODO DEMO" in final_content:
                print("   ⚠️  Vídeo gerado em MODO DEMO")
                print("   ℹ️  quick_generate.py precisa estar disponível para produção")
                result = "DEMO"
            elif "SUCESSO" in final_content:
                print("   ✅ Vídeo gerado com SUCESSO!")

                # Extrair informações
                if "Arquivo:" in final_content:
                    print("   ✅ Arquivo de vídeo criado")
                if "Cenas:" in final_content:
                    print("   ✅ Cenas processadas")
                if "Custo:" in final_content:
                    print("   ✅ Custo calculado")

                result = "SUCCESS"
            else:
                print("   ❌ Resultado não identificado")
                result = "UNKNOWN"

            # Relatório final
            print(f"\n{'='*70}")
            print(f"📋 RELATÓRIO DO TESTE")
            print(f"{'='*70}")
            print(f"🌐 URL testada: {url}")
            print(f"🎭 Modo: {'DEMO' if is_demo else 'PRODUÇÃO'}")
            print(f"📊 Resultado: {result}")
            print(f"📸 Screenshots: test_results/01-03_*.png")
            print(f"⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")

            if result == "DEMO":
                print("⚠️  ATENÇÃO:")
                print("   O sistema ainda está em modo demo.")
                print("   Aguarde o deploy completar (~2-3 min após o push).")
                print("   Execute este teste novamente em alguns minutos.\n")
            elif result == "SUCCESS":
                print("🎉 SUCESSO!")
                print("   O deploy está funcionando perfeitamente!")
                print("   Vídeos estão sendo gerados em produção.\n")

        except Exception as e:
            print(f"\n❌ ERRO durante o teste:")
            print(f"   {str(e)}")
            await page.screenshot(path="test_results/error.png")
            print("   Screenshot do erro salvo em test_results/error.png")

        finally:
            # Fechar navegador
            await browser.close()
            print("🏁 Teste finalizado.\n")


if __name__ == "__main__":
    # Criar diretório de resultados
    os.makedirs("test_results", exist_ok=True)

    # Executar teste
    asyncio.run(test_oma_cloudrun())
