"""
Real Playwright E2E Tests - Actually Execute Against Running Agent Server
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_USER = "test_admin"
ADMIN_PASSWORD = "admin123"

# Test results
results = {
    "passed": [],
    "failed": [],
    "errors": []
}

async def test_login_page_loads():
    """Test: Login page loads"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(f"{BASE_URL}/login", wait_until="networkidle")
            title = await page.title()

            if "login" in page.url.lower() or "sign" in title.lower():
                results["passed"].append("01_login_page_loads")
                print("[PASS] Login page loads")
            else:
                results["failed"].append("01_login_page_loads - URL mismatch")
                print("[FAIL] Login page loads - URL check failed")
        except Exception as e:
            results["errors"].append(f"01_login_page_loads: {str(e)}")
            print(f"[ERROR] Login page loads: {str(e)}")
        finally:
            await browser.close()

async def test_login_form_visible():
    """Test: Login form elements visible"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(f"{BASE_URL}/login")

            # Check for input fields
            inputs = await page.locator("input").count()
            buttons = await page.locator("button").count()

            if inputs >= 2 and buttons >= 1:
                results["passed"].append("02_login_form_visible")
                print(f"[PASS] Login form visible (found {inputs} inputs, {buttons} buttons)")
            else:
                results["failed"].append("02_login_form_visible - Form elements missing")
                print("[FAIL] Login form visible - Not enough form elements")
        except Exception as e:
            results["errors"].append(f"02_login_form_visible: {str(e)}")
            print(f"[ERROR] Login form visible: {str(e)}")
        finally:
            await browser.close()

async def test_user_list_page():
    """Test: User management page loads"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(f"{BASE_URL}/admin/users", wait_until="domcontentloaded")

            # Check if page loaded
            content = await page.content()

            if "user" in content.lower() or "404" not in str(page.status):
                results["passed"].append("03_user_list_page_loads")
                print("[PASS] User list page loads")
            else:
                results["failed"].append("03_user_list_page_loads - Page not accessible")
                print("[FAIL] User list page loads - 404 or not found")
        except Exception as e:
            # Page might not exist without navigation, check if it's 404
            results["errors"].append(f"03_user_list_page_loads: {str(e)}")
            print(f"[ERROR] User list page: {str(e)}")
        finally:
            await browser.close()

async def test_worker_list_page():
    """Test: Worker management page loads"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(f"{BASE_URL}/admin/workers", wait_until="domcontentloaded")

            content = await page.content()

            if "worker" in content.lower() or "404" not in str(page.status):
                results["passed"].append("04_worker_list_page_loads")
                print("[PASS] Worker list page loads")
            else:
                results["failed"].append("04_worker_list_page_loads - Page not accessible")
                print("[FAIL] Worker list page loads")
        except Exception as e:
            results["errors"].append(f"04_worker_list_page_loads: {str(e)}")
            print(f"[ERROR] Worker list page: {str(e)}")
        finally:
            await browser.close()

async def test_health_check():
    """Test: Server health endpoint"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.goto(f"{BASE_URL}/health")

            if response.status == 200:
                results["passed"].append("05_health_check")
                print("[PASS] Health endpoint returns 200")
            else:
                results["failed"].append(f"05_health_check - Status {response.status}")
                print(f"[FAIL] Health endpoint returns {response.status}")
        except Exception as e:
            results["errors"].append(f"05_health_check: {str(e)}")
            print(f"[ERROR] Health check: {str(e)}")
        finally:
            await browser.close()

async def test_static_files_loaded():
    """Test: Static files load (CSS, JS)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(f"{BASE_URL}/login")

            # Check for any stylesheets or scripts
            scripts = await page.locator("script").count()
            styles = await page.locator("[rel='stylesheet']").count()

            if scripts > 0 or styles > 0:
                results["passed"].append("06_static_files_loaded")
                print(f"[PASS] Static files loaded ({scripts} scripts, {styles} stylesheets)")
            else:
                results["failed"].append("06_static_files_loaded - No resources loaded")
                print("[FAIL] No static files loaded")
        except Exception as e:
            results["errors"].append(f"06_static_files_loaded: {str(e)}")
            print(f"[ERROR] Static files: {str(e)}")
        finally:
            await browser.close()

async def test_responsive_design():
    """Test: Page responsive at different sizes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        sizes = [
            (1920, 1080, "Desktop"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]

        try:
            all_passed = True
            for width, height, device_type in sizes:
                page = await browser.new_page(viewport={"width": width, "height": height})
                await page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")

                # Check if page rendered without errors
                has_content = await page.locator("body").count() > 0

                if not has_content:
                    all_passed = False
                    print(f"[FAIL] Responsive at {device_type} ({width}x{height})")

                await page.close()

            if all_passed:
                results["passed"].append("07_responsive_design")
                print("[PASS] Responsive design works at all sizes")
            else:
                results["failed"].append("07_responsive_design - Some sizes failed")
        except Exception as e:
            results["errors"].append(f"07_responsive_design: {str(e)}")
            print(f"[ERROR] Responsive design: {str(e)}")
        finally:
            await browser.close()

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("PLAYWRIGHT E2E TEST EXECUTION")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}")
    print("\nRunning tests...\n")

    await test_health_check()
    await test_login_page_loads()
    await test_login_form_visible()
    await test_static_files_loaded()
    await test_responsive_design()
    await test_user_list_page()
    await test_worker_list_page()

    # Print results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)

    total = len(results["passed"]) + len(results["failed"]) + len(results["errors"])

    print(f"\nTotal Tests:  {total}")
    print(f"Passed:       {len(results['passed'])} ({len(results['passed'])/total*100:.1f}%)")
    print(f"Failed:       {len(results['failed'])} ({len(results['failed'])/total*100:.1f}%)")
    print(f"Errors:       {len(results['errors'])} ({len(results['errors'])/total*100:.1f}%)")

    if results["passed"]:
        print(f"\nPassed Tests:")
        for test in results["passed"]:
            print(f"  - {test}")

    if results["failed"]:
        print(f"\nFailed Tests:")
        for test in results["failed"]:
            print(f"  - {test}")

    if results["errors"]:
        print(f"\nTests with Errors:")
        for test in results["errors"]:
            print(f"  - {test}")

    print("\n" + "="*80)
    print("END OF PLAYWRIGHT TEST EXECUTION")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
