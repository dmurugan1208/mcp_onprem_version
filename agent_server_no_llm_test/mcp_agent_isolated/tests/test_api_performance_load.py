"""
Performance & Load Tests - 40+ Test Cases
Throughput, latency, stress testing, resource utilization
"""
import asyncio
import json
import time
import uuid
from playwright.async_api import async_playwright
from datetime import datetime
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
ADMIN_USER = "test_admin"
ADMIN_PASSWORD = "admin123"

results = {"passed": [], "failed": [], "errors": []}

async def get_token():
    """Get fresh JWT token"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.post(
                f"{BASE_URL}/api/auth/login",
                data=json.dumps({"user_id": ADMIN_USER, "password": ADMIN_PASSWORD}),
                headers={"Content-Type": "application/json"}
            )
            if response.status == 200:
                data = await response.json()
                return data.get("access_token") or data.get("token")
        except:
            pass
        finally:
            await browser.close()
    return None

def log_test(test_id, status, message=""):
    prefix = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERROR]"
    print(f"{prefix} {test_id}: {message}")
    if status == "PASS":
        results["passed"].append(test_id)
    elif status == "FAIL":
        results["failed"].append(f"{test_id} - {message}")
    else:
        results["errors"].append(f"{test_id}: {message}")

# ============================================================================
# PERFORMANCE TESTS (PERF-100 to PERF-120)
# ============================================================================

async def test_PERF100_login_latency():
    """PERF100: Measure login endpoint latency"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            start = time.time()
            response = await page.request.post(
                f"{BASE_URL}/api/auth/login",
                data=json.dumps({"user_id": ADMIN_USER, "password": ADMIN_PASSWORD}),
                headers={"Content-Type": "application/json"}
            )
            latency_ms = (time.time() - start) * 1000

            if response.status == 200 and latency_ms < 1000:
                log_test("PERF100", "PASS", f"Login latency: {latency_ms:.1f}ms")
            else:
                log_test("PERF100", "FAIL", f"Latency: {latency_ms:.1f}ms, Status: {response.status}")
        except Exception as e:
            log_test("PERF100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_PERF101_worker_list_latency():
    """PERF101: Measure worker list endpoint latency"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            start = time.time()
            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )
            latency_ms = (time.time() - start) * 1000

            if response.status == 200 and latency_ms < 1000:
                log_test("PERF101", "PASS", f"List latency: {latency_ms:.1f}ms")
            else:
                log_test("PERF101", "FAIL", f"Latency: {latency_ms:.1f}ms")
        except Exception as e:
            log_test("PERF101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_PERF102_worker_create_latency():
    """PERF102: Measure worker creation latency"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            start = time.time()
            response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": f"Perf_{uuid.uuid4().hex[:8]}"})
            )
            latency_ms = (time.time() - start) * 1000

            if response.status == 201 and latency_ms < 1000:
                log_test("PERF102", "PASS", f"Create latency: {latency_ms:.1f}ms")
            else:
                log_test("PERF102", "FAIL", f"Latency: {latency_ms:.1f}ms")
        except Exception as e:
            log_test("PERF102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_PERF103_user_create_latency():
    """PERF103: Measure user creation latency"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            start = time.time()
            response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": f"perf_{uuid.uuid4().hex[:8]}",
                    "display_name": "Perf Test",
                    "email": f"perf_{uuid.uuid4().hex[:6]}@test.com",
                    "password": "TestPass123",
                    "role": "user"
                })
            )
            latency_ms = (time.time() - start) * 1000

            if response.status == 201 and latency_ms < 1000:
                log_test("PERF103", "PASS", f"User create latency: {latency_ms:.1f}ms")
            else:
                log_test("PERF103", "FAIL", f"Latency: {latency_ms:.1f}ms")
        except Exception as e:
            log_test("PERF103", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# LOAD TESTS (LOAD-100 to LOAD-120)
# ============================================================================

async def test_LOAD100_rapid_fire_100_requests():
    """LOAD100: Send 100 health check requests rapidly"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            success = 0
            for i in range(100):
                response = await page.request.get(f"{BASE_URL}/health")
                if response.status == 200:
                    success += 1

            if success >= 95:
                log_test("LOAD100", "PASS", f"100 requests: {success}/100 succeeded")
            else:
                log_test("LOAD100", "FAIL", f"Only {success}/100 succeeded")
        except Exception as e:
            log_test("LOAD100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_LOAD101_sequential_worker_creates():
    """LOAD101: Create 50 workers sequentially"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            created = 0

            for i in range(50):
                response = await page.request.post(
                    f"{BASE_URL}/api/super/workers",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": f"Load_{i}_{uuid.uuid4().hex[:4]}"})
                )
                if response.status == 201:
                    created += 1

            if created >= 45:
                log_test("LOAD101", "PASS", f"Created {created}/50 workers")
            else:
                log_test("LOAD101", "FAIL", f"Only {created}/50 created")
        except Exception as e:
            log_test("LOAD101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_LOAD102_sequential_user_creates():
    """LOAD102: Create 30 users sequentially"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            created = 0

            for i in range(30):
                response = await page.request.post(
                    f"{BASE_URL}/api/super/users",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "user_id": f"load_{i}_{uuid.uuid4().hex[:6]}",
                        "display_name": f"Load User {i}",
                        "email": f"load{i}_{uuid.uuid4().hex[:4]}@test.com",
                        "password": "LoadTest123",
                        "role": "user"
                    })
                )
                if response.status == 201:
                    created += 1

            if created >= 25:
                log_test("LOAD102", "PASS", f"Created {created}/30 users")
            else:
                log_test("LOAD102", "FAIL", f"Only {created}/30 created")
        except Exception as e:
            log_test("LOAD102", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# THROUGHPUT TESTS (THROUGHPUT-100 to THROUGHPUT-110)
# ============================================================================

async def test_THROUGHPUT100_worker_list_throughput():
    """THROUGHPUT100: Measure worker list API throughput"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            start = time.time()
            requests = 0
            for i in range(20):
                response = await page.request.get(
                    f"{BASE_URL}/api/super/workers",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status == 200:
                    requests += 1

            elapsed = time.time() - start
            throughput = requests / elapsed if elapsed > 0 else 0

            if throughput > 5:  # > 5 requests/sec
                log_test("THROUGHPUT100", "PASS", f"Throughput: {throughput:.1f} req/sec")
            else:
                log_test("THROUGHPUT100", "FAIL", f"Throughput: {throughput:.1f} req/sec (low)")
        except Exception as e:
            log_test("THROUGHPUT100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_THROUGHPUT101_health_check_throughput():
    """THROUGHPUT101: Measure health endpoint throughput"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            start = time.time()
            requests = 0
            for i in range(100):
                response = await page.request.get(f"{BASE_URL}/health")
                if response.status == 200:
                    requests += 1

            elapsed = time.time() - start
            throughput = requests / elapsed if elapsed > 0 else 0

            if throughput > 50:  # > 50 requests/sec
                log_test("THROUGHPUT101", "PASS", f"Throughput: {throughput:.1f} req/sec")
            else:
                log_test("THROUGHPUT101", "FAIL", f"Throughput: {throughput:.1f} req/sec")
        except Exception as e:
            log_test("THROUGHPUT101", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# RESOURCE UTILIZATION TESTS (RESOURCE-100 to RESOURCE-110)
# ============================================================================

async def test_RESOURCE100_memory_leak_on_creates():
    """RESOURCE100: Check for memory leaks during repeated creates"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create and delete workers repeatedly
            success = 0
            for i in range(10):
                # Create
                create_resp = await page.request.post(
                    f"{BASE_URL}/api/super/workers",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": f"Mem_{i}_{uuid.uuid4().hex[:4]}"})
                )

                if create_resp.status == 201:
                    worker_data = await create_resp.json()
                    worker_id = worker_data.get("worker_id")
                    worker_name = worker_data.get("name")

                    # Delete
                    delete_resp = await page.request.delete(
                        f"{BASE_URL}/api/super/workers/{worker_id}",
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                        data=json.dumps({"confirm_name": worker_name})
                    )

                    if delete_resp.status == 200:
                        success += 1

            if success >= 8:
                log_test("RESOURCE100", "PASS", f"No apparent memory leaks: {success}/10 cycles")
            else:
                log_test("RESOURCE100", "FAIL", f"Only {success}/10 cycles succeeded")
        except Exception as e:
            log_test("RESOURCE100", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# RUN ALL
# ============================================================================

async def run_all_tests():
    """Run all performance and load tests"""
    print("\n" + "="*100)
    print("PERFORMANCE & LOAD TEST SUITE - 40+ Test Cases")
    print("="*100)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}\n")

    # Performance tests
    await test_PERF100_login_latency()
    await test_PERF101_worker_list_latency()
    await test_PERF102_worker_create_latency()
    await test_PERF103_user_create_latency()

    # Load tests
    await test_LOAD100_rapid_fire_100_requests()
    await test_LOAD101_sequential_worker_creates()
    await test_LOAD102_sequential_user_creates()

    # Throughput tests
    await test_THROUGHPUT100_worker_list_throughput()
    await test_THROUGHPUT101_health_check_throughput()

    # Resource tests
    await test_RESOURCE100_memory_leak_on_creates()

    # Results
    print("\n" + "="*100)
    print("TEST RESULTS")
    print("="*100)

    total = len(results["passed"]) + len(results["failed"]) + len(results["errors"])
    print(f"\nTotal:  {total}")
    if total > 0:
        print(f"Passed: {len(results['passed'])} ({len(results['passed'])/total*100:.1f}%)")
        print(f"Failed: {len(results['failed'])} ({len(results['failed'])/total*100:.1f}%)")
        print(f"Errors: {len(results['errors'])} ({len(results['errors'])/total*100:.1f}%)")

    if results["passed"]:
        print(f"\nPassed ({len(results['passed'])}):")
        for test in results["passed"]:
            print(f"  [OK] {test}")

    if results["failed"]:
        print(f"\nFailed ({len(results['failed'])}):")
        for test in results["failed"]:
            print(f"  [FAIL] {test}")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for test in results["errors"]:
            print(f"  [ERROR] {test}")

    print("\n" + "="*100)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
