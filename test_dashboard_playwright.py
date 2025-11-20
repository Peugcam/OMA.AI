"""
Test Dashboard with Playwright
Analyze why it's not opening properly
"""
import asyncio
from playwright.async_api import async_playwright
import time
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

async def test_dashboard():
    print("🔍 Starting Playwright analysis...")

    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"📝 Console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"❌ Error: {err}"))

        try:
            print("\n🌐 Navigating to http://localhost:7860...")
            response = await page.goto("http://localhost:7860", timeout=30000)

            print(f"✅ Response status: {response.status}")
            print(f"✅ Response URL: {response.url}")

            # Wait for page to load
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Take screenshot
            await page.screenshot(path="dashboard_screenshot.png")
            print("📸 Screenshot saved: dashboard_screenshot.png")

            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")

            # Check for Gradio app
            gradio_app = await page.query_selector("gradio-app")
            if gradio_app:
                print("✅ Gradio app found!")
            else:
                print("⚠️ Gradio app NOT found")

            # Get page content
            content = await page.content()
            print(f"\n📝 Page HTML length: {len(content)} characters")

            # Check for errors in the page
            errors = await page.evaluate("""
                () => {
                    return {
                        hasGradioError: document.querySelector('.error-message') !== null,
                        bodyText: document.body.innerText.substring(0, 500)
                    }
                }
            """)

            print(f"\n📊 Page Analysis:")
            print(f"  - Has Gradio Error: {errors['hasGradioError']}")
            print(f"  - Body Text Preview: {errors['bodyText'][:200]}...")

            # Wait a bit more to see if content loads
            print("\n⏳ Waiting 5 seconds for dynamic content...")
            await asyncio.sleep(5)

            # Check again
            await page.screenshot(path="dashboard_screenshot_after.png")
            print("📸 Second screenshot saved: dashboard_screenshot_after.png")

            # Get all visible text
            visible_text = await page.evaluate("document.body.innerText")
            print(f"\n📄 Visible text on page:\n{visible_text[:1000]}")

            # Check network activity
            print("\n🌐 Checking network activity...")

            # Get all iframes
            frames = page.frames
            print(f"\n🖼️ Found {len(frames)} frames")
            for i, frame in enumerate(frames):
                print(f"  Frame {i}: {frame.url}")

        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            await page.screenshot(path="dashboard_error.png")
            print("📸 Error screenshot saved: dashboard_error.png")

        finally:
            await browser.close()
            print("\n✅ Playwright analysis complete!")

if __name__ == "__main__":
    asyncio.run(test_dashboard())
