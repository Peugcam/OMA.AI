"""
Analyze Dashboard Performance and Visual Issues
Detecta problemas de rendering, tremor, etc.
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

async def analyze_dashboard():
    print("🔍 Analisando Dashboard - Problemas de Rendering")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Vamos ver o dashboard
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = await context.new_page()

        # Monitorar console
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"❌ Page Error: {err}"))

        try:
            print("\n🌐 Carregando dashboard...")
            await page.goto("http://localhost:7861", wait_until="domcontentloaded", timeout=30000)

            print("⏳ Aguardando carregamento completo...")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(3)

            print("✅ Dashboard carregado!\n")

            # Screenshot inicial
            await page.screenshot(path="dashboard_initial.png", full_page=True)
            print("📸 Screenshot inicial: dashboard_initial.png")

            # Verificar performance metrics
            print("\n📊 Métricas de Performance:")
            metrics = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        pageLoad: timing.loadEventEnd - timing.navigationStart,
                        domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
                    };
                }
            """)

            print(f"  - Page Load: {metrics.get('pageLoad', 0)}ms")
            print(f"  - DOM Ready: {metrics.get('domReady', 0)}ms")
            print(f"  - First Paint: {metrics.get('firstPaint', 0)}ms")

            # Verificar elementos que podem estar causando tremor
            print("\n🔍 Verificando elementos problemáticos:")

            # Verificar animações CSS
            animations = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    let animatedElements = [];

                    elements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        if (styles.animation !== 'none' || styles.transition !== 'all 0s ease 0s') {
                            animatedElements.push({
                                tag: el.tagName,
                                animation: styles.animation,
                                transition: styles.transition
                            });
                        }
                    });

                    return animatedElements.slice(0, 10); // Primeiros 10
                }
            """)

            if animations:
                print(f"  ⚠️ Encontrados {len(animations)} elementos com animação/transição")
                for i, anim in enumerate(animations[:5]):
                    print(f"     {i+1}. {anim['tag']}: {anim.get('animation', 'N/A')[:50]}")
            else:
                print("  ✅ Sem animações CSS detectadas")

            # Verificar problemas de layout shift
            print("\n🎯 Testando Layout Shift:")

            # Scroll suave para ver se treme
            for i in range(3):
                await page.mouse.wheel(0, 200)
                await asyncio.sleep(0.5)
                await page.screenshot(path=f"scroll_test_{i}.png")
                print(f"  📸 Screenshot scroll {i+1}: scroll_test_{i}.png")

            # Voltar ao topo
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # Verificar iframes
            print("\n🖼️ Verificando iframes:")
            frames = page.frames
            print(f"  - Total de frames: {len(frames)}")
            for i, frame in enumerate(frames):
                print(f"     Frame {i}: {frame.url[:80]}")

            # Verificar recursos carregando
            print("\n📦 Verificando recursos:")
            resources = await page.evaluate("""
                () => {
                    return performance.getEntriesByType('resource').map(r => ({
                        name: r.name.split('/').pop(),
                        duration: r.duration,
                        size: r.transferSize
                    })).filter(r => r.duration > 100);
                }
            """)

            if resources:
                print(f"  ⚠️ {len(resources)} recursos lentos (>100ms):")
                for r in resources[:5]:
                    print(f"     - {r['name'][:40]}: {r['duration']:.0f}ms, {r['size']}bytes")
            else:
                print("  ✅ Todos os recursos carregam rapidamente")

            # Verificar JavaScript errors
            print("\n⚠️ Console Logs:")
            errors = [log for log in console_logs if 'error' in log.lower() or 'warning' in log.lower()]
            if errors:
                print(f"  Encontrados {len(errors)} erros/warnings:")
                for err in errors[:5]:
                    print(f"     - {err}")
            else:
                print("  ✅ Sem erros no console")

            # Testar interação
            print("\n🖱️ Testando interações:")

            # Procurar dropdown de templates
            try:
                dropdown = await page.query_selector("select, [role='combobox']")
                if dropdown:
                    print("  ✅ Dropdown encontrado")

                    # Hover sobre o dropdown
                    await dropdown.hover()
                    await asyncio.sleep(0.5)
                    await page.screenshot(path="hover_test.png")
                    print("  📸 Screenshot hover: hover_test.png")

                    # Clicar
                    await dropdown.click()
                    await asyncio.sleep(1)
                    await page.screenshot(path="click_test.png")
                    print("  📸 Screenshot click: click_test.png")
                else:
                    print("  ⚠️ Dropdown não encontrado")
            except Exception as e:
                print(f"  ⚠️ Erro ao testar dropdown: {e}")

            # Verificar CPU usage via Performance Observer
            print("\n💻 Verificando uso de recursos:")
            cpu_intensive = await page.evaluate("""
                () => {
                    const entries = performance.getEntriesByType('measure');
                    return entries.length;
                }
            """)
            print(f"  - Performance measures: {cpu_intensive}")

            # Gravar vídeo por 10 segundos
            print("\n🎥 Gravando vídeo de 10 segundos para análise...")

            # Criar novo contexto com vídeo
            video_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir="videos/",
                record_video_size={"width": 1920, "height": 1080}
            )
            video_page = await video_context.new_page()

            await video_page.goto("http://localhost:7861", wait_until="networkidle")
            await asyncio.sleep(3)

            # Interagir um pouco
            await video_page.mouse.move(500, 500)
            await asyncio.sleep(2)
            await video_page.mouse.wheel(0, 300)
            await asyncio.sleep(2)
            await video_page.mouse.move(800, 400)
            await asyncio.sleep(3)

            await video_context.close()
            print("  ✅ Vídeo salvo em: videos/")

            # Screenshot final
            await page.screenshot(path="dashboard_final.png", full_page=True)
            print("\n📸 Screenshot final: dashboard_final.png")

            print("\n" + "="*60)
            print("📋 RESUMO DA ANÁLISE")
            print("="*60)

            issues_found = []

            if len(animations) > 20:
                issues_found.append("⚠️ Muitas animações CSS detectadas")

            if len([log for log in console_logs if 'error' in log.lower()]) > 0:
                issues_found.append("❌ Erros JavaScript no console")

            if len(resources) > 10:
                issues_found.append("⚠️ Muitos recursos lentos")

            if not issues_found:
                print("✅ DASHBOARD ESTÁ SAUDÁVEL!")
                print("\nPossíveis causas do tremor:")
                print("  1. Hardware acelerado do navegador")
                print("  2. Animações do Gradio (normais)")
                print("  3. Renderização de elementos dinâmicos")
                print("\nSoluções:")
                print("  - Desabilite animações no CSS")
                print("  - Use tema mais simples do Gradio")
                print("  - Reduza componentes na página")
            else:
                print("⚠️ PROBLEMAS ENCONTRADOS:")
                for issue in issues_found:
                    print(f"  {issue}")

            print("\n📊 Arquivos gerados para análise:")
            print("  - dashboard_initial.png")
            print("  - dashboard_final.png")
            print("  - scroll_test_0.png, scroll_test_1.png, scroll_test_2.png")
            print("  - hover_test.png, click_test.png")
            print("  - videos/ (gravação de 10s)")

            # Manter aberto por 15 segundos para você ver
            print("\n⏸️ Mantendo navegador aberto por 15 segundos...")
            print("   (observe se está tremendo)")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n❌ Erro durante análise: {e}")
            await page.screenshot(path="error_analysis.png")

        finally:
            await browser.close()
            print("\n✅ Análise completa!")

if __name__ == "__main__":
    asyncio.run(analyze_dashboard())
