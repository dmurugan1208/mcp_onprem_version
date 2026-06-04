"""
Test Agent Server CRUD operations without SAJHA server.
Tests user and worker management through agent server API endpoints.
"""
import httpx
import json
import asyncio
import uuid
from typing import Optional

BASE_URL = "http://localhost:8000"
ADMIN_USER = "test_admin"
ADMIN_PASSWORD = "admin123"  # Default test password

# Track JWT token
TOKEN = None


async def login() -> bool:
    """Login as super_admin and get JWT token."""
    global TOKEN

    print("\n" + "="*60)
    print("STEP 1: LOGIN")
    print("="*60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={"user_id": ADMIN_USER, "password": ADMIN_PASSWORD}
            )

            if response.status_code == 200:
                data = response.json()
                TOKEN = data.get("access_token") or data.get("token")
                print(f"Login successful for {ADMIN_USER}")
                print(f"Token: {TOKEN[:20]}...")
                return True
            else:
                print(f"Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False


def get_headers() -> dict:
    """Get authorization headers."""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


async def test_worker_crud():
    """Test Worker CRUD operations."""
    print("\n" + "="*60)
    print("TEST: Worker CRUD Operations")
    print("="*60)

    async with httpx.AsyncClient() as client:
        # CREATE Worker
        print("\n[CREATE] Creating new worker...")
        create_req = {
            "name": "Test CRUD Worker",
            "description": "Created by agent server test",
            "system_prompt": "You are a test worker",
            "enabled_tools": ["tool1", "tool2"]
        }

        response = await client.post(
            f"{BASE_URL}/api/super/workers",
            json=create_req,
            headers=get_headers()
        )

        if response.status_code == 201:
            worker = response.json()
            worker_id = worker.get('worker_id')  # Capture returned ID
            print(f"SUCCESS: Worker created")
            print(f"  - ID: {worker_id}")
            print(f"  - Name: {worker.get('name')}")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        # READ Worker
        print("\n[READ] Getting worker details...")
        response = await client.get(
            f"{BASE_URL}/api/super/workers/{worker_id}",
            headers=get_headers()
        )

        if response.status_code == 200:
            worker = response.json()
            print(f"SUCCESS: Worker retrieved")
            print(f"  - ID: {worker.get('worker_id')}")
            print(f"  - Name: {worker.get('name')}")
            print(f"  - Description: {worker.get('description')}")
        else:
            print(f"FAILED: {response.status_code}")
            return False

        # UPDATE Worker
        print("\n[UPDATE] Updating worker...")
        update_req = {
            "name": "Test CRUD Worker (Updated)",
            "description": "Updated by agent server test"
        }

        response = await client.put(
            f"{BASE_URL}/api/super/workers/{worker_id}",
            json=update_req,
            headers=get_headers()
        )

        if response.status_code == 200:
            worker = response.json()
            print(f"SUCCESS: Worker updated")
            print(f"  - Name: {worker.get('name')}")
            print(f"  - Description: {worker.get('description')}")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        # LIST Workers
        print("\n[LIST] Getting all workers...")
        response = await client.get(
            f"{BASE_URL}/api/super/workers",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            workers = data.get('workers', [])
            print(f"SUCCESS: Retrieved {len(workers)} workers")
            test_worker = next((w for w in workers if w.get('worker_id') == worker_id), None)
            if test_worker:
                print(f"  - Test worker found in list")
        else:
            print(f"FAILED: {response.status_code}")
            return False

        # DELETE Worker
        print("\n[DELETE] Deleting worker...")
        delete_req = {
            "confirm_name": "Test CRUD Worker (Updated)"  # Must match actual worker name
        }
        response = await client.request(
            "DELETE",
            f"{BASE_URL}/api/super/workers/{worker_id}",
            json=delete_req,
            headers=get_headers()
        )

        if response.status_code == 200:
            print(f"SUCCESS: Worker deleted")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        return True


async def test_user_crud():
    """Test User CRUD operations."""
    print("\n" + "="*60)
    print("TEST: User CRUD Operations")
    print("="*60)

    async with httpx.AsyncClient() as client:
        # CREATE User
        print("\n[CREATE] Creating new user...")
        user_id = f"test_crud_{uuid.uuid4().hex[:8]}"  # Unique user ID
        create_req = {
            "user_id": user_id,
            "display_name": "Test CRUD User",
            "email": "testcrud@example.com",
            "password": "TestPassword123!",
            "role": "user"
        }

        response = await client.post(
            f"{BASE_URL}/api/super/users",
            json=create_req,
            headers=get_headers()
        )

        if response.status_code == 201:
            user = response.json()
            print(f"SUCCESS: User created")
            print(f"  - ID: {user.get('user_id')}")
            print(f"  - Display Name: {user.get('display_name')}")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        # READ User (via LIST since there's no individual GET endpoint)
        print("\n[READ] Getting user details (from list)...")
        response = await client.get(
            f"{BASE_URL}/api/super/users",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            found_user = next((u for u in users if u.get('user_id') == user_id), None)
            if found_user:
                print(f"SUCCESS: User retrieved")
                print(f"  - ID: {found_user.get('user_id')}")
                print(f"  - Display Name: {found_user.get('display_name')}")
                print(f"  - Role: {found_user.get('role')}")
            else:
                print(f"FAILED: User not found in list")
                return False
        else:
            print(f"FAILED: {response.status_code}")
            return False

        # UPDATE User
        print("\n[UPDATE] Updating user...")
        update_req = {
            "display_name": "Test CRUD User (Updated)"
        }

        response = await client.put(
            f"{BASE_URL}/api/super/users/{user_id}",
            json=update_req,
            headers=get_headers()
        )

        if response.status_code == 200:
            user = response.json()
            print(f"SUCCESS: User updated")
            print(f"  - Display Name: {user.get('display_name')}")
            print(f"  - Role: {user.get('role')}")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        # LIST Users
        print("\n[LIST] Getting all users...")
        response = await client.get(
            f"{BASE_URL}/api/super/users",
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"SUCCESS: Retrieved {len(users)} users")
            test_user = next((u for u in users if u.get('user_id') == user_id), None)
            if test_user:
                print(f"  - Test user found in list")
        else:
            print(f"FAILED: {response.status_code}")
            return False

        # DELETE User
        print("\n[DELETE] Deleting user...")
        response = await client.request(
            "DELETE",
            f"{BASE_URL}/api/super/users/{user_id}",
            headers=get_headers()
        )

        if response.status_code == 200:
            print(f"SUCCESS: User deleted")
        else:
            print(f"FAILED: {response.status_code}")
            print(f"  {response.text}")
            return False

        return True


async def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# AGENT SERVER CRUD TEST (WITHOUT SAJHA SERVER)")
    print("# Testing standalone agent for user and worker management")
    print("#"*60)

    # Login
    if not await login():
        print("\nCannot proceed - login failed")
        return

    # Run tests
    results = {
        'Worker CRUD': await test_worker_crud(),
        'User CRUD': await test_user_crud(),
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}")

    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("SUCCESS!")
        print("Agent server can manage workers and users INDEPENDENTLY")
        print("WITHOUT running SAJHA server.")
    else:
        print("FAILED: Some tests did not pass")
    print("="*60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
