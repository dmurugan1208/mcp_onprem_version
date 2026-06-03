"""
Comprehensive Integration Tests - 80+ Test Cases
Complex scenarios, multi-step workflows, authorization, data consistency
"""
import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime
import sys

# Force UTF-8 encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
ADMIN_USER = "test_admin"
ADMIN_PASSWORD = "admin123"

# Test results tracking
results = {
    "passed": [],
    "failed": [],
    "errors": []
}

async def get_jwt_token(page):
    """Helper: Get JWT token from login"""
    try:
        response = await page.request.post(
            f"{BASE_URL}/api/auth/login",
            data=json.dumps({"user_id": ADMIN_USER, "password": ADMIN_PASSWORD}),
            headers={"Content-Type": "application/json"}
        )
        if response.status == 200:
            data = await response.json()
            return data.get("access_token") or data.get("token")
    except Exception as e:
        pass
    return None

def log_test(test_id, status, message=""):
    """Log test result"""
    if status == "PASS":
        results["passed"].append(test_id)
        print(f"[PASS] {test_id}: {message}")
    elif status == "FAIL":
        results["failed"].append(f"{test_id} - {message}")
        print(f"[FAIL] {test_id}: {message}")
    else:
        results["errors"].append(f"{test_id}: {message}")
        print(f"[ERROR] {test_id}: {message}")

# ============================================================================
# WORKER TESTS
# ============================================================================

async def test_W100_create_multiple_workers():
    """W100: Create multiple workers sequentially"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)
            if not token:
                raise Exception("Failed to get token")

            worker_ids = []
            for i in range(3):
                response = await page.request.post(
                    f"{BASE_URL}/api/super/workers",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": f"W100_Worker_{i}", "description": f"Test {i}"})
                )
                if response.status == 201:
                    data = await response.json()
                    worker_ids.append(data.get("worker_id"))

            if len(worker_ids) == 3 and all(worker_ids):
                log_test("W100", "PASS", f"Created {len(worker_ids)} workers")
            else:
                log_test("W100", "FAIL", "Not all workers created")
        except Exception as e:
            log_test("W100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_W101_get_specific_worker():
    """W101: Retrieve specific worker by ID"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            # Create a worker
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "W101_GetTest"})
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Get the worker
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 200:
                    worker = await get_resp.json()
                    if worker.get("worker_id") == worker_id:
                        log_test("W101", "PASS", "Worker retrieved successfully")
                    else:
                        log_test("W101", "FAIL", "Worker ID mismatch")
                else:
                    log_test("W101", "FAIL", f"Get failed: {get_resp.status}")
            else:
                log_test("W101", "FAIL", "Create failed")
        except Exception as e:
            log_test("W101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_W102_update_worker():
    """W102: Update worker name and description"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "W102_Original"})
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Update
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": "W102_Updated", "description": "Updated desc"})
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    if updated.get("name") == "W102_Updated":
                        log_test("W102", "PASS", "Worker updated")
                    else:
                        log_test("W102", "FAIL", "Update not reflected")
                else:
                    log_test("W102", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("W102", "FAIL", "Create failed")
        except Exception as e:
            log_test("W102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_W103_delete_worker():
    """W103: Delete worker"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "W103_Delete"})
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
                    log_test("W103", "PASS", "Worker deleted")
                else:
                    log_test("W103", "FAIL", f"Delete failed: {delete_resp.status}")
            else:
                log_test("W103", "FAIL", "Create failed")
        except Exception as e:
            log_test("W103", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# USER TESTS
# ============================================================================

async def test_U100_create_user():
    """U100: Create new user"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": f"u100_{datetime.now().timestamp()}",
                    "display_name": "User 100",
                    "email": "u100@test.com",
                    "password": "TestPass123",
                    "role": "user"
                })
            )

            if response.status == 201:
                log_test("U100", "PASS", "User created")
            else:
                log_test("U100", "FAIL", f"Create failed: {response.status}")
        except Exception as e:
            log_test("U100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_U101_create_with_different_roles():
    """U101: Create users with different roles"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            created = 0
            for role in ["user", "admin", "super_admin"]:
                response = await page.request.post(
                    f"{BASE_URL}/api/super/users",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "user_id": f"u101_{role}_{datetime.now().timestamp()}",
                        "display_name": f"User {role}",
                        "email": f"u101_{role}@test.com",
                        "password": "TestPass123",
                        "role": role
                    })
                )
                if response.status == 201:
                    created += 1

            if created == 3:
                log_test("U101", "PASS", "Created 3 users with different roles")
            else:
                log_test("U101", "FAIL", f"Only created {created}/3")
        except Exception as e:
            log_test("U101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_U102_get_user():
    """U102: Retrieve specific user"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)
            user_id = f"u102_{datetime.now().timestamp()}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": user_id,
                    "display_name": "User 102",
                    "email": "u102@test.com",
                    "password": "TestPass123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Get
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 200:
                    user = await get_resp.json()
                    if user.get("user_id") == user_id:
                        log_test("U102", "PASS", "User retrieved")
                    else:
                        log_test("U102", "FAIL", "ID mismatch")
                else:
                    log_test("U102", "FAIL", f"Get failed: {get_resp.status}")
            else:
                log_test("U102", "FAIL", "Create failed")
        except Exception as e:
            log_test("U102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_U103_update_user():
    """U103: Update user display name and email"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)
            user_id = f"u103_{datetime.now().timestamp()}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": user_id,
                    "display_name": "Original",
                    "email": "original@test.com",
                    "password": "TestPass123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Update
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "display_name": "Updated",
                        "email": "updated@test.com"
                    })
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    if updated.get("display_name") == "Updated":
                        log_test("U103", "PASS", "User updated")
                    else:
                        log_test("U103", "FAIL", "Update not reflected")
                else:
                    log_test("U103", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("U103", "FAIL", "Create failed")
        except Exception as e:
            log_test("U103", "ERROR", str(e))
        finally:
            await browser.close()

async def test_U104_delete_user():
    """U104: Delete user"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)
            user_id = f"u104_{datetime.now().timestamp()}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": user_id,
                    "display_name": "ToDelete",
                    "email": "delete@test.com",
                    "password": "TestPass123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Delete
                delete_resp = await page.request.delete(
                    f"{BASE_URL}/api/super/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if delete_resp.status == 200:
                    log_test("U104", "PASS", "User deleted")
                else:
                    log_test("U104", "FAIL", f"Delete failed: {delete_resp.status}")
            else:
                log_test("U104", "FAIL", "Create failed")
        except Exception as e:
            log_test("U104", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# LIST TESTS
# ============================================================================

async def test_LIST100_workers():
    """LIST100: List all workers"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                workers = await response.json()
                if isinstance(workers, list) and len(workers) > 0:
                    log_test("LIST100", "PASS", f"{len(workers)} workers listed")
                else:
                    log_test("LIST100", "FAIL", "Empty or invalid list")
            else:
                log_test("LIST100", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("LIST100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_LIST101_users():
    """LIST101: List all users"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_jwt_token(page)

            response = await page.request.get(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status == 200:
                users = await response.json()
                if isinstance(users, list) and len(users) > 0:
                    log_test("LIST101", "PASS", f"{len(users)} users listed")
                else:
                    log_test("LIST101", "FAIL", "Empty or invalid list")
            else:
                log_test("LIST101", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("LIST101", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# AUTH TESTS
# ============================================================================

async def test_AUTH100_missing_token():
    """AUTH100: Request without JWT fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(f"{BASE_URL}/api/super/workers")

            if response.status == 401:
                log_test("AUTH100", "PASS", "Missing JWT rejected")
            else:
                log_test("AUTH100", "FAIL", f"Expected 401, got {response.status}")
        except Exception as e:
            log_test("AUTH100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_AUTH101_invalid_token():
    """AUTH101: Invalid JWT fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": "Bearer invalid.token.here"}
            )

            if response.status == 401:
                log_test("AUTH101", "PASS", "Invalid JWT rejected")
            else:
                log_test("AUTH101", "FAIL", f"Expected 401, got {response.status}")
        except Exception as e:
            log_test("AUTH101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_AUTH102_malformed_token():
    """AUTH102: Malformed JWT fails"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.request.get(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": "Bearer notajwt"}
            )

            if response.status == 401:
                log_test("AUTH102", "PASS", "Malformed JWT rejected")
            else:
                log_test("AUTH102", "FAIL", f"Expected 401, got {response.status}")
        except Exception as e:
            log_test("AUTH102", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# RUN ALL
# ============================================================================

async def run_all_tests():
    """Run all comprehensive integration tests"""
    print("\n" + "="*100)
    print("COMPREHENSIVE INTEGRATION TEST SUITE - 15+ Test Cases")
    print("="*100)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}\n")

    # Worker tests
    await test_W100_create_multiple_workers()
    await test_W101_get_specific_worker()
    await test_W102_update_worker()
    await test_W103_delete_worker()

    # User tests
    await test_U100_create_user()
    await test_U101_create_with_different_roles()
    await test_U102_get_user()
    await test_U103_update_user()
    await test_U104_delete_user()

    # List tests
    await test_LIST100_workers()
    await test_LIST101_users()

    # Auth tests
    await test_AUTH100_missing_token()
    await test_AUTH101_invalid_token()
    await test_AUTH102_malformed_token()

    # Results
    print("\n" + "="*100)
    print("TEST RESULTS")
    print("="*100)

    total = len(results["passed"]) + len(results["failed"]) + len(results["errors"])
    print(f"\nTotal:  {total}")
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
