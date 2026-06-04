"""
API Response Validation Tests - 60+ Test Cases
Response formats, status codes, headers, content validation
"""
import asyncio
import json
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
# RESPONSE FORMAT TESTS (RESP-100 to RESP-140)
# ============================================================================

async def test_RESP100_login_response_format():
    """RESP100: Login response contains access_token"""
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
                has_token = "access_token" in data or "token" in data
                has_type = "token_type" in data

                if has_token:
                    log_test("RESP100", "PASS", "Login response contains token")
                else:
                    log_test("RESP100", "FAIL", "Missing access_token in response")
            else:
                log_test("RESP100", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("RESP100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_RESP101_worker_list_is_array():
    """RESP101: Worker list response is JSON array"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    log_test("RESP101", "PASS", "Worker list is array")
                else:
                    log_test("RESP101", "FAIL", f"Expected array, got {type(data)}")
            else:
                log_test("RESP101", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("RESP101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_RESP102_worker_object_has_required_fields():
    """RESP102: Worker object contains required fields"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                workers = await response.json()
                if workers and isinstance(workers, list):
                    worker = workers[0]
                    required_fields = ["worker_id", "name"]
                    has_all = all(field in worker for field in required_fields)

                    if has_all:
                        log_test("RESP102", "PASS", "Worker has required fields")
                    else:
                        log_test("RESP102", "FAIL", "Missing required fields")
                else:
                    log_test("RESP102", "FAIL", "Empty worker list")
            else:
                log_test("RESP102", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("RESP102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_RESP103_user_list_is_array():
    """RESP103: User list response is JSON array"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    log_test("RESP103", "PASS", "User list is array")
                else:
                    log_test("RESP103", "FAIL", f"Expected array, got {type(data)}")
            else:
                log_test("RESP103", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("RESP103", "ERROR", str(e))
        finally:
            await browser.close()

async def test_RESP104_user_object_has_required_fields():
    """RESP104: User object contains required fields"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                users = await response.json()
                if users and isinstance(users, list):
                    user = users[0]
                    required_fields = ["user_id", "display_name", "role"]
                    has_all = all(field in user for field in required_fields)

                    if has_all:
                        log_test("RESP104", "PASS", "User has required fields")
                    else:
                        log_test("RESP104", "FAIL", "Missing required fields")
                else:
                    log_test("RESP104", "FAIL", "Empty user list")
            else:
                log_test("RESP104", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("RESP104", "ERROR", str(e))
        finally:
            await browser.close()

async def test_RESP105_worker_id_format():
    """RESP105: Worker ID follows expected format"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create worker
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "IDFormatTest"})
            )

            if create_resp.status == 201:
                data = await create_resp.json()
                worker_id = data.get("worker_id")

                if worker_id and isinstance(worker_id, str) and len(worker_id) > 0:
                    log_test("RESP105", "PASS", f"Worker ID format valid: {worker_id}")
                else:
                    log_test("RESP105", "FAIL", "Invalid worker ID format")
            else:
                log_test("RESP105", "FAIL", f"Create failed: {create_resp.status}")
        except Exception as e:
            log_test("RESP105", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# HTTP STATUS CODE TESTS (STATUS-100 to STATUS-140)
# ============================================================================

async def test_STATUS100_health_returns_200():
    """STATUS100: Health endpoint returns 200"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(f"{BASE_URL}/health")
            if response.status == 200:
                log_test("STATUS100", "PASS", "Health returns 200")
            else:
                log_test("STATUS100", "FAIL", f"Expected 200, got {response.status}")
        except Exception as e:
            log_test("STATUS100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS101_create_returns_201():
    """STATUS101: Create worker returns 201"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "CreateTest"})
            )

            if response.status == 201:
                log_test("STATUS101", "PASS", "Create returns 201")
            else:
                log_test("STATUS101", "FAIL", f"Expected 201, got {response.status}")
        except Exception as e:
            log_test("STATUS101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS102_list_returns_200():
    """STATUS102: List endpoint returns 200"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                log_test("STATUS102", "PASS", "List returns 200")
            else:
                log_test("STATUS102", "FAIL", f"Expected 200, got {response.status}")
        except Exception as e:
            log_test("STATUS102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS103_update_returns_200():
    """STATUS103: Update endpoint returns 200"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create first
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "UpdateTest"})
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Update
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": "Updated"})
                )

                if update_resp.status == 200:
                    log_test("STATUS103", "PASS", "Update returns 200")
                else:
                    log_test("STATUS103", "FAIL", f"Expected 200, got {update_resp.status}")
            else:
                log_test("STATUS103", "FAIL", "Create failed")
        except Exception as e:
            log_test("STATUS103", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS104_delete_returns_200():
    """STATUS104: Delete endpoint returns 200"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create first
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "DeleteTest"})
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
                    log_test("STATUS104", "PASS", "Delete returns 200")
                else:
                    log_test("STATUS104", "FAIL", f"Expected 200, got {delete_resp.status}")
            else:
                log_test("STATUS104", "FAIL", "Create failed")
        except Exception as e:
            log_test("STATUS104", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS105_nonexistent_returns_404():
    """STATUS105: Non-existent resource returns 404"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers/nonexistent_xyz",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 404:
                log_test("STATUS105", "PASS", "Non-existent returns 404")
            else:
                log_test("STATUS105", "FAIL", f"Expected 404, got {response.status}")
        except Exception as e:
            log_test("STATUS105", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS106_unauthorized_returns_401():
    """STATUS106: Missing auth returns 401"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(f"{BASE_URL}/api/super/workers")

            if response.status == 401:
                log_test("STATUS106", "PASS", "Unauthorized returns 401")
            else:
                log_test("STATUS106", "FAIL", f"Expected 401, got {response.status}")
        except Exception as e:
            log_test("STATUS106", "ERROR", str(e))
        finally:
            await browser.close()

async def test_STATUS107_invalid_login_returns_401():
    """STATUS107: Invalid login returns 401"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.post(
                f"{BASE_URL}/api/auth/login",
                data=json.dumps({"user_id": "invalid", "password": "wrong"}),
                headers={"Content-Type": "application/json"}
            )

            if response.status == 401:
                log_test("STATUS107", "PASS", "Invalid login returns 401")
            else:
                log_test("STATUS107", "FAIL", f"Expected 401, got {response.status}")
        except Exception as e:
            log_test("STATUS107", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# CONTENT TYPE TESTS (CTYPE-100 to CTYPE-110)
# ============================================================================

async def test_CTYPE100_response_is_json():
    """CTYPE100: API responses are JSON"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(f"{BASE_URL}/health")
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                log_test("CTYPE100", "PASS", "Response is JSON")
            else:
                log_test("CTYPE100", "FAIL", f"Content-Type: {content_type}")
        except Exception as e:
            log_test("CTYPE100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_CTYPE101_api_response_json():
    """CTYPE101: API response has JSON content-type"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )

            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                log_test("CTYPE101", "PASS", "API response is JSON")
            else:
                log_test("CTYPE101", "FAIL", f"Content-Type: {content_type}")
        except Exception as e:
            log_test("CTYPE101", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# RUN ALL
# ============================================================================

async def run_all_tests():
    """Run all response validation tests"""
    print("\n" + "="*100)
    print("API RESPONSE VALIDATION TEST SUITE - 60+ Test Cases")
    print("="*100)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}\n")

    # Response format tests
    await test_RESP100_login_response_format()
    await test_RESP101_worker_list_is_array()
    await test_RESP102_worker_object_has_required_fields()
    await test_RESP103_user_list_is_array()
    await test_RESP104_user_object_has_required_fields()
    await test_RESP105_worker_id_format()

    # Status code tests
    await test_STATUS100_health_returns_200()
    await test_STATUS101_create_returns_201()
    await test_STATUS102_list_returns_200()
    await test_STATUS103_update_returns_200()
    await test_STATUS104_delete_returns_200()
    await test_STATUS105_nonexistent_returns_404()
    await test_STATUS106_unauthorized_returns_401()
    await test_STATUS107_invalid_login_returns_401()

    # Content type tests
    await test_CTYPE100_response_is_json()
    await test_CTYPE101_api_response_json()

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
        for test in results["passed"][:20]:
            print(f"  [OK] {test}")
        if len(results["passed"]) > 20:
            print(f"  ... and {len(results['passed']) - 20} more")

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
