"""
Comprehensive Playwright Tests for Agent Server REST API
Tests all API endpoints with real HTTP requests
"""
import asyncio
import json
import uuid
from playwright.async_api import async_playwright
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_USER = "test_admin"
ADMIN_PASSWORD = "admin123"

results = {
    "passed": [],
    "failed": [],
    "errors": []
}

# Global JWT token
JWT_TOKEN = None

async def test_001_health_endpoint():
    """Test: Health endpoint returns 200"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.goto(f"{BASE_URL}/health")
            content = await page.content()

            if response.status == 200 and "ok" in content.lower():
                results["passed"].append("001_health_endpoint")
                print("[PASS] Health endpoint: 200 OK")
            else:
                results["failed"].append("001_health_endpoint")
                print(f"[FAIL] Health endpoint: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"001: {str(e)}")
            print(f"[ERROR] Health endpoint: {str(e)}")
        finally:
            await browser.close()

async def test_002_login_api():
    """Test: Login API endpoint"""
    global JWT_TOKEN

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Make API request
            response = await page.request.post(
                f"{BASE_URL}/api/auth/login",
                data=json.dumps({
                    "user_id": ADMIN_USER,
                    "password": ADMIN_PASSWORD
                }),
                headers={"Content-Type": "application/json"}
            )

            if response.status == 200:
                data = await response.json()
                JWT_TOKEN = data.get("access_token") or data.get("token")

                if JWT_TOKEN:
                    results["passed"].append("002_login_api")
                    print("[PASS] Login API: 200 OK, JWT received")
                else:
                    results["failed"].append("002_login_api - No JWT in response")
                    print("[FAIL] Login API: No JWT token in response")
            else:
                results["failed"].append(f"002_login_api - Status {response.status}")
                print(f"[FAIL] Login API: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"002: {str(e)}")
            print(f"[ERROR] Login API: {str(e)}")
        finally:
            await browser.close()

async def test_003_invalid_login():
    """Test: Invalid login fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.request.post(
                f"{BASE_URL}/api/auth/login",
                data=json.dumps({
                    "user_id": "invalid_user",
                    "password": "wrong_password"
                }),
                headers={"Content-Type": "application/json"}
            )

            if response.status in [401, 403, 400]:
                results["passed"].append("003_invalid_login")
                print(f"[PASS] Invalid login rejected: {response.status}")
            else:
                results["failed"].append(f"003_invalid_login - Status {response.status}")
                print(f"[FAIL] Invalid login should fail, got {response.status}")
        except Exception as e:
            results["errors"].append(f"003: {str(e)}")
            print(f"[ERROR] Invalid login test: {str(e)}")
        finally:
            await browser.close()

async def test_004_list_workers():
    """Test: List workers API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {JWT_TOKEN}"}
            )

            if response.status == 200:
                data = await response.json()

                if isinstance(data, dict) and "workers" in data:
                    worker_count = len(data["workers"])
                    results["passed"].append("004_list_workers")
                    print(f"[PASS] List workers: {worker_count} workers returned")
                elif isinstance(data, list):
                    results["passed"].append("004_list_workers")
                    print(f"[PASS] List workers: {len(data)} workers returned")
                else:
                    results["failed"].append("004_list_workers - Wrong response format")
                    print("[FAIL] List workers: Wrong response format")
            else:
                results["failed"].append(f"004_list_workers - Status {response.status}")
                print(f"[FAIL] List workers: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"004: {str(e)}")
            print(f"[ERROR] List workers: {str(e)}")
        finally:
            await browser.close()

async def test_005_list_users():
    """Test: List users API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {JWT_TOKEN}"}
            )

            if response.status == 200:
                data = await response.json()

                if isinstance(data, dict) and "users" in data:
                    user_count = len(data["users"])
                    results["passed"].append("005_list_users")
                    print(f"[PASS] List users: {user_count} users returned")
                else:
                    results["failed"].append("005_list_users - Wrong format")
                    print("[FAIL] List users: Wrong response format")
            else:
                results["failed"].append(f"005_list_users - Status {response.status}")
                print(f"[FAIL] List users: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"005: {str(e)}")
            print(f"[ERROR] List users: {str(e)}")
        finally:
            await browser.close()

async def test_006_create_worker():
    """Test: Create worker API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            worker_data = {
                "name": f"Test Worker {uuid.uuid4().hex[:8]}",
                "description": "E2E test worker",
                "system_prompt": "You are a test worker",
                "enabled_tools": ["tool1", "tool2"]
            }

            response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                data=json.dumps(worker_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if response.status == 201:
                data = await response.json()
                worker_id = data.get("worker_id")

                if worker_id:
                    results["passed"].append("006_create_worker")
                    print(f"[PASS] Create worker: {worker_id} created")
                else:
                    results["failed"].append("006_create_worker - No worker_id")
                    print("[FAIL] Create worker: No worker_id in response")
            else:
                results["failed"].append(f"006_create_worker - Status {response.status}")
                print(f"[FAIL] Create worker: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"006: {str(e)}")
            print(f"[ERROR] Create worker: {str(e)}")
        finally:
            await browser.close()

async def test_007_create_user():
    """Test: Create user API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            user_id = f"e2e_user_{uuid.uuid4().hex[:8]}"
            user_data = {
                "user_id": user_id,
                "display_name": "E2E Test User",
                "email": "e2e@example.com",
                "password": "TestPassword123!",
                "role": "user"
            }

            response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                data=json.dumps(user_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if response.status == 201:
                data = await response.json()

                if data.get("user_id") == user_id:
                    results["passed"].append("007_create_user")
                    print(f"[PASS] Create user: {user_id} created")
                else:
                    results["failed"].append("007_create_user - User ID mismatch")
                    print("[FAIL] Create user: User ID mismatch")
            else:
                results["failed"].append(f"007_create_user - Status {response.status}")
                print(f"[FAIL] Create user: Status {response.status}")
        except Exception as e:
            results["errors"].append(f"007: {str(e)}")
            print(f"[ERROR] Create user: {str(e)}")
        finally:
            await browser.close()

async def test_008_get_worker():
    """Test: Get single worker API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # First get list to get a worker ID
            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {JWT_TOKEN}"}
            )

            if response.status == 200:
                data = await response.json()
                workers = data.get("workers", [])

                if workers:
                    worker_id = workers[0].get("worker_id")

                    # Get specific worker
                    get_response = await page.request.get(
                        f"{BASE_URL}/api/super/workers/{worker_id}",
                        headers={"Authorization": f"Bearer {JWT_TOKEN}"}
                    )

                    if get_response.status == 200:
                        worker = await get_response.json()

                        if worker.get("worker_id") == worker_id:
                            results["passed"].append("008_get_worker")
                            print(f"[PASS] Get worker: {worker_id} retrieved")
                        else:
                            results["failed"].append("008_get_worker - ID mismatch")
                            print("[FAIL] Get worker: ID mismatch")
                    else:
                        results["failed"].append(f"008_get_worker - Status {get_response.status}")
                        print(f"[FAIL] Get worker: Status {get_response.status}")
        except Exception as e:
            results["errors"].append(f"008: {str(e)}")
            print(f"[ERROR] Get worker: {str(e)}")
        finally:
            await browser.close()

async def test_009_update_worker():
    """Test: Update worker API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Create a worker to update
            worker_data = {
                "name": f"Original Name {uuid.uuid4().hex[:4]}",
                "description": "Test worker"
            }

            create_response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                data=json.dumps(worker_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if create_response.status == 201:
                created = await create_response.json()
                worker_id = created.get("worker_id")

                # Update the worker
                update_data = {"name": "Updated Name"}
                update_response = await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    data=json.dumps(update_data),
                    headers={
                        "Authorization": f"Bearer {JWT_TOKEN}",
                        "Content-Type": "application/json"
                    }
                )

                if update_response.status == 200:
                    updated = await update_response.json()

                    if updated.get("name") == "Updated Name":
                        results["passed"].append("009_update_worker")
                        print(f"[PASS] Update worker: {worker_id} updated")
                    else:
                        results["failed"].append("009_update_worker - Name not updated")
                        print("[FAIL] Update worker: Name not changed")
                else:
                    results["failed"].append(f"009_update_worker - Status {update_response.status}")
                    print(f"[FAIL] Update worker: Status {update_response.status}")
        except Exception as e:
            results["errors"].append(f"009: {str(e)}")
            print(f"[ERROR] Update worker: {str(e)}")
        finally:
            await browser.close()

async def test_010_delete_worker():
    """Test: Delete worker API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Create a worker to delete
            worker_data = {
                "name": f"Delete Test {uuid.uuid4().hex[:4]}",
                "description": "To be deleted"
            }

            create_response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                data=json.dumps(worker_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if create_response.status == 201:
                created = await create_response.json()
                worker_id = created.get("worker_id")
                worker_name = created.get("name")

                # Delete the worker
                delete_response = await page.request.delete(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    data=json.dumps({"confirm_name": worker_name}),
                    headers={
                        "Authorization": f"Bearer {JWT_TOKEN}",
                        "Content-Type": "application/json"
                    }
                )

                if delete_response.status == 200:
                    results["passed"].append("010_delete_worker")
                    print(f"[PASS] Delete worker: {worker_id} deleted")
                else:
                    results["failed"].append(f"010_delete_worker - Status {delete_response.status}")
                    print(f"[FAIL] Delete worker: Status {delete_response.status}")
        except Exception as e:
            results["errors"].append(f"010: {str(e)}")
            print(f"[ERROR] Delete worker: {str(e)}")
        finally:
            await browser.close()

async def test_011_update_user():
    """Test: Update user API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            user_id = f"e2e_update_{uuid.uuid4().hex[:8]}"

            # Create a user
            user_data = {
                "user_id": user_id,
                "display_name": "Original Name",
                "email": "test@example.com",
                "password": "Test123!",
                "role": "user"
            }

            create_response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                data=json.dumps(user_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if create_response.status == 201:
                # Update the user
                update_data = {"display_name": "Updated Name"}
                update_response = await page.request.put(
                    f"{BASE_URL}/api/super/users/{user_id}",
                    data=json.dumps(update_data),
                    headers={
                        "Authorization": f"Bearer {JWT_TOKEN}",
                        "Content-Type": "application/json"
                    }
                )

                if update_response.status == 200:
                    updated = await update_response.json()

                    if updated.get("display_name") == "Updated Name":
                        results["passed"].append("011_update_user")
                        print(f"[PASS] Update user: {user_id} updated")
                    else:
                        results["failed"].append("011_update_user - Name not updated")
                        print("[FAIL] Update user: Name not changed")
                else:
                    results["failed"].append(f"011_update_user - Status {update_response.status}")
                    print(f"[FAIL] Update user: Status {update_response.status}")
        except Exception as e:
            results["errors"].append(f"011: {str(e)}")
            print(f"[ERROR] Update user: {str(e)}")
        finally:
            await browser.close()

async def test_012_delete_user():
    """Test: Delete user API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            user_id = f"e2e_delete_{uuid.uuid4().hex[:8]}"

            # Create a user
            user_data = {
                "user_id": user_id,
                "display_name": "To Delete",
                "email": "delete@example.com",
                "password": "Test123!",
                "role": "user"
            }

            create_response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                data=json.dumps(user_data),
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                }
            )

            if create_response.status == 201:
                # Delete the user
                delete_response = await page.request.delete(
                    f"{BASE_URL}/api/super/users/{user_id}",
                    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
                )

                if delete_response.status == 200:
                    results["passed"].append("012_delete_user")
                    print(f"[PASS] Delete user: {user_id} deleted")
                else:
                    results["failed"].append(f"012_delete_user - Status {delete_response.status}")
                    print(f"[FAIL] Delete user: Status {delete_response.status}")
        except Exception as e:
            results["errors"].append(f"012: {str(e)}")
            print(f"[ERROR] Delete user: {str(e)}")
        finally:
            await browser.close()

async def test_013_unauthorized_access():
    """Test: Unauthorized access fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": "Bearer invalid_token"}
            )

            if response.status in [401, 403]:
                results["passed"].append("013_unauthorized_access")
                print(f"[PASS] Unauthorized access rejected: {response.status}")
            else:
                results["failed"].append(f"013_unauthorized_access - Status {response.status}")
                print(f"[FAIL] Unauthorized access should fail, got {response.status}")
        except Exception as e:
            results["errors"].append(f"013: {str(e)}")
            print(f"[ERROR] Unauthorized test: {str(e)}")
        finally:
            await browser.close()

async def test_014_missing_jwt():
    """Test: Missing JWT fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={}
            )

            if response.status in [401, 403]:
                results["passed"].append("014_missing_jwt")
                print(f"[PASS] Missing JWT rejected: {response.status}")
            else:
                results["failed"].append(f"014_missing_jwt - Status {response.status}")
                print(f"[FAIL] Missing JWT should fail, got {response.status}")
        except Exception as e:
            results["errors"].append(f"014: {str(e)}")
            print(f"[ERROR] Missing JWT test: {str(e)}")
        finally:
            await browser.close()

async def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*100)
    print("COMPREHENSIVE PLAYWRIGHT API TESTS")
    print("="*100)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}")
    print(f"Test User: {ADMIN_USER}\n")

    # Run tests in order
    print("Running tests...\n")

    await test_001_health_endpoint()
    await test_002_login_api()
    await test_003_invalid_login()
    await test_004_list_workers()
    await test_005_list_users()
    await test_006_create_worker()
    await test_007_create_user()
    await test_008_get_worker()
    await test_009_update_worker()
    await test_010_delete_worker()
    await test_011_update_user()
    await test_012_delete_user()
    await test_013_unauthorized_access()
    await test_014_missing_jwt()

    # Print summary
    print("\n" + "="*100)
    print("TEST RESULTS SUMMARY")
    print("="*100)

    total = len(results["passed"]) + len(results["failed"]) + len(results["errors"])
    pass_rate = len(results["passed"]) / total * 100 if total > 0 else 0

    print(f"\nTotal Tests:      {total}")
    print(f"Passed:           {len(results['passed'])} ({pass_rate:.1f}%)")
    print(f"Failed:           {len(results['failed'])} ({len(results['failed'])/total*100:.1f}%)")
    print(f"Errors:           {len(results['errors'])} ({len(results['errors'])/total*100:.1f}%)")

    if pass_rate >= 90:
        verdict = "EXCELLENT"
    elif pass_rate >= 70:
        verdict = "GOOD"
    elif pass_rate >= 50:
        verdict = "ACCEPTABLE"
    else:
        verdict = "NEEDS IMPROVEMENT"

    print(f"\nVerdict:          {verdict}")

    print("\n" + "-"*100)
    print("PASSED TESTS")
    print("-"*100)
    for test in results["passed"]:
        print(f"  [OK] {test}")

    if results["failed"]:
        print("\n" + "-"*100)
        print("FAILED TESTS")
        print("-"*100)
        for test in results["failed"]:
            print(f"  [FAIL] {test}")

    if results["errors"]:
        print("\n" + "-"*100)
        print("TESTS WITH ERRORS")
        print("-"*100)
        for test in results["errors"]:
            print(f"  [ERROR] {test}")

    print("\n" + "="*100)
    print("END OF TEST EXECUTION")
    print("="*100 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
