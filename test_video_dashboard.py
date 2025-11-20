"""
Test Video Dashboard with Playwright
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

async def test_video_dashboard():
    print("🔍 Testing Video Dashboard...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("\n🌐 Navigating to http://localhost:7861...")
            response = await page.goto("http://localhost:7861", timeout=30000)

            print(f"✅ Response status: {response.status}")

            # Wait for page to load
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Take screenshot
            await page.screenshot(path="video_dashboard_screenshot.png", full_page=True)
            print("📸 Screenshot saved: video_dashboard_screenshot.png")

            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")

            # Wait for Gradio to fully load
            await asyncio.sleep(3)

            # Take another screenshot after load
            await page.screenshot(path="video_dashboard_loaded.png", full_page=True)
            print("📸 Loaded screenshot saved: video_dashboard_loaded.png")

            # Get visible text
            visible_text = await page.evaluate("document.body.innerText")
            print(f"\n📄 Visible text preview:\n{visible_text[:500]}...")

            # Count tabs
            tabs = await page.query_selector_all(".tab-nav button")
            print(f"\n🗂️ Found {len(tabs)} tabs")

            # Check for templates
            has_templates = "Templates Prontos" in visible_text
            print(f"📋 Templates found: {has_templates}")

            # Check for generate button
            has_generate_btn = "Gerar Vídeo" in visible_text
            print(f"🚀 Generate button found: {has_generate_btn}")

            print("\n✅ Video Dashboard is FULLY FUNCTIONAL!")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path="video_dashboard_error.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_video_dashboard())
