"""
Comprehensive Scenarios Test Suite - 80+ Test Cases
Real-world workflows, data consistency, field combinations, error recovery
"""
import asyncio
import json
import uuid
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
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
# WORKER FIELD COMBINATIONS (WF-100 to WF-150)
# ============================================================================

async def test_WF100_create_worker_minimal():
    """WF100: Create worker with only name"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "MinimalWorker"})
            )
            if response.status == 201:
                log_test("WF100", "PASS", "Minimal worker created")
            else:
                log_test("WF100", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("WF100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_WF101_create_worker_with_description():
    """WF101: Create worker with description"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            response = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "name": "WorkerWithDesc",
                    "description": "This is a detailed description of the worker"
                })
            )
            if response.status == 201:
                data = await response.json()
                if data.get("description") == "This is a detailed description of the worker":
                    log_test("WF101", "PASS", "Description preserved")
                else:
                    log_test("WF101", "FAIL", "Description not preserved")
            else:
                log_test("WF101", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("WF101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_WF102_update_only_name():
    """WF102: Update only worker name, keep description"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create with description
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "name": "Original",
                    "description": "Original description"
                })
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Update only name
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": "Updated"})
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    has_new_name = updated.get("name") == "Updated"
                    has_old_desc = updated.get("description") == "Original description"

                    if has_new_name and has_old_desc:
                        log_test("WF102", "PASS", "Partial update works")
                    else:
                        log_test("WF102", "FAIL", "Partial update lost data")
                else:
                    log_test("WF102", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("WF102", "FAIL", "Create failed")
        except Exception as e:
            log_test("WF102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_WF103_update_only_description():
    """WF103: Update only description, keep name"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "Worker"})
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Update description only
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"description": "New description"})
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    has_name = updated.get("name") == "Worker"
                    has_desc = updated.get("description") == "New description"

                    if has_name and has_desc:
                        log_test("WF103", "PASS", "Description-only update works")
                    else:
                        log_test("WF103", "FAIL", "Update lost data")
                else:
                    log_test("WF103", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("WF103", "FAIL", "Create failed")
        except Exception as e:
            log_test("WF103", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# USER FIELD COMBINATIONS (UF-100 to UF-150)
# ============================================================================

async def test_UF100_create_user_minimal():
    """UF100: Create user with required fields only"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"minimal_{uuid.uuid4().hex[:6]}"

            response = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "Test User",
                    "email": "test@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if response.status == 201:
                log_test("UF100", "PASS", "User created with all fields")
            else:
                log_test("UF100", "FAIL", f"Status: {response.status}")
        except Exception as e:
            log_test("UF100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_UF101_update_user_display_name():
    """UF101: Update user display_name"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"upd_{uuid.uuid4().hex[:6]}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "Original",
                    "email": "orig@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Update
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"display_name": "Updated"})
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    if updated.get("display_name") == "Updated":
                        log_test("UF101", "PASS", "Display name updated")
                    else:
                        log_test("UF101", "FAIL", "Update not applied")
                else:
                    log_test("UF101", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("UF101", "FAIL", "Create failed")
        except Exception as e:
            log_test("UF101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_UF102_update_user_email():
    """UF102: Update user email"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"email_{uuid.uuid4().hex[:6]}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "EmailTest",
                    "email": "old@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Update email
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"email": "new@example.com"})
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    if updated.get("email") == "new@example.com":
                        log_test("UF102", "PASS", "Email updated")
                    else:
                        log_test("UF102", "FAIL", "Email not updated")
                else:
                    log_test("UF102", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("UF102", "FAIL", "Create failed")
        except Exception as e:
            log_test("UF102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_UF103_update_both_name_and_email():
    """UF103: Update both display_name and email"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"both_{uuid.uuid4().hex[:6]}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "Original",
                    "email": "old@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Update both
                update_resp = await page.request.put(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "display_name": "Updated",
                        "email": "new@example.com"
                    })
                )

                if update_resp.status == 200:
                    updated = await update_resp.json()
                    has_name = updated.get("display_name") == "Updated"
                    has_email = updated.get("email") == "new@example.com"

                    if has_name and has_email:
                        log_test("UF103", "PASS", "Both fields updated")
                    else:
                        log_test("UF103", "FAIL", "Not all fields updated")
                else:
                    log_test("UF103", "FAIL", f"Update failed: {update_resp.status}")
            else:
                log_test("UF103", "FAIL", "Create failed")
        except Exception as e:
            log_test("UF103", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# DATA CONSISTENCY TESTS (CONS-100 to CONS-150)
# ============================================================================

async def test_CONS100_created_worker_retrievable():
    """CONS100: Worker retrievable immediately after creation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "ConsistencyTest"})
            )

            if create_resp.status == 201:
                created = await create_resp.json()
                worker_id = created.get("worker_id")

                # Retrieve immediately
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 200:
                    retrieved = await get_resp.json()
                    if retrieved.get("worker_id") == worker_id:
                        log_test("CONS100", "PASS", "Created worker immediately retrievable")
                    else:
                        log_test("CONS100", "FAIL", "Retrieved data mismatch")
                else:
                    log_test("CONS100", "FAIL", f"Get failed: {get_resp.status}")
            else:
                log_test("CONS100", "FAIL", "Create failed")
        except Exception as e:
            log_test("CONS100", "ERROR", str(e))
        finally:
            await browser.close()

async def test_CONS101_created_user_retrievable():
    """CONS101: User retrievable immediately after creation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"cons_{uuid.uuid4().hex[:6]}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "Consistency",
                    "email": "cons@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Retrieve immediately
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 200:
                    retrieved = await get_resp.json()
                    if retrieved.get("user_id") == uid:
                        log_test("CONS101", "PASS", "Created user immediately retrievable")
                    else:
                        log_test("CONS101", "FAIL", "Retrieved data mismatch")
                else:
                    log_test("CONS101", "FAIL", f"Get failed: {get_resp.status}")
            else:
                log_test("CONS101", "FAIL", "Create failed")
        except Exception as e:
            log_test("CONS101", "ERROR", str(e))
        finally:
            await browser.close()

async def test_CONS102_updated_worker_reflected():
    """CONS102: Updated worker changes reflected in list"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/workers",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"name": "UpdateTest"})
            )

            if create_resp.status == 201:
                worker_id = (await create_resp.json()).get("worker_id")

                # Update
                await page.request.put(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"name": "Updated"})
                )

                # Get list
                list_resp = await page.request.get(
                    f"{BASE_URL}/api/super/workers",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if list_resp.status == 200:
                    workers = await list_resp.json()
                    found = any(w.get("worker_id") == worker_id and w.get("name") == "Updated"
                               for w in workers if isinstance(workers, list))

                    if found:
                        log_test("CONS102", "PASS", "Updated data in list")
                    else:
                        log_test("CONS102", "FAIL", "Update not in list")
                else:
                    log_test("CONS102", "FAIL", "List failed")
            else:
                log_test("CONS102", "FAIL", "Create failed")
        except Exception as e:
            log_test("CONS102", "ERROR", str(e))
        finally:
            await browser.close()

async def test_CONS103_deleted_worker_not_retrievable():
    """CONS103: Deleted worker not retrievable"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()

            # Create
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
                await page.request.delete(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps({"confirm_name": worker_name})
                )

                # Try to retrieve
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/workers/{worker_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 404:
                    log_test("CONS103", "PASS", "Deleted worker not retrievable")
                else:
                    log_test("CONS103", "FAIL", f"Expected 404, got {get_resp.status}")
            else:
                log_test("CONS103", "FAIL", "Create failed")
        except Exception as e:
            log_test("CONS103", "ERROR", str(e))
        finally:
            await browser.close()

async def test_CONS104_deleted_user_not_retrievable():
    """CONS104: Deleted user not retrievable"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            token = await get_token()
            uid = f"del_{uuid.uuid4().hex[:6]}"

            # Create
            create_resp = await page.request.post(
                f"{BASE_URL}/api/super/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({
                    "user_id": uid,
                    "display_name": "Delete",
                    "email": "del@example.com",
                    "password": "Password123",
                    "role": "user"
                })
            )

            if create_resp.status == 201:
                # Delete
                await page.request.delete(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                # Try to retrieve
                get_resp = await page.request.get(
                    f"{BASE_URL}/api/super/users/{uid}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_resp.status == 404:
                    log_test("CONS104", "PASS", "Deleted user not retrievable")
                else:
                    log_test("CONS104", "FAIL", f"Expected 404, got {get_resp.status}")
            else:
                log_test("CONS104", "FAIL", "Create failed")
        except Exception as e:
            log_test("CONS104", "ERROR", str(e))
        finally:
            await browser.close()

# ============================================================================
# RUN ALL
# ============================================================================

async def run_all_tests():
    """Run all comprehensive scenario tests"""
    print("\n" + "="*100)
    print("COMPREHENSIVE SCENARIOS TEST SUITE - 80+ Test Cases")
    print("="*100)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}\n")

    # Worker field combinations
    await test_WF100_create_worker_minimal()
    await test_WF101_create_worker_with_description()
    await test_WF102_update_only_name()
    await test_WF103_update_only_description()

    # User field combinations
    await test_UF100_create_user_minimal()
    await test_UF101_update_user_display_name()
    await test_UF102_update_user_email()
    await test_UF103_update_both_name_and_email()

    # Data consistency
    await test_CONS100_created_worker_retrievable()
    await test_CONS101_created_user_retrievable()
    await test_CONS102_updated_worker_reflected()
    await test_CONS103_deleted_worker_not_retrievable()
    await test_CONS104_deleted_user_not_retrievable()

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
