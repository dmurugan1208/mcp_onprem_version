"""
Test CRUD operations on Worker and User repositories.
Demonstrates that agent can independently create, read, update, delete workers/users.
"""
import sys
import os
from pathlib import Path
import json
import copy

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.repository import WorkerRepository, UserRepository


def test_worker_crud():
    """Test WorkerRepository CRUD operations"""
    print("\n" + "="*60)
    print("TEST 1: WorkerRepository CRUD Operations")
    print("="*60)

    repo = WorkerRepository()

    # Backup original
    original_workers = repo.list()
    print(f"Original count: {len(original_workers)} workers")

    # CREATE
    try:
        new_worker = {
            'worker_id': 'w-test-agent-crud',
            'name': 'Agent CRUD Test Worker',
            'description': 'Created by agent CRUD test',
            'enabled_tools': ['tool1', 'tool2'],
            'agent_mode': 'single',
            'enabled': True
        }
        created = repo.create(new_worker)
        print(f"\nCREATE: Successfully created worker")
        print(f"  - ID: {created['worker_id']}")
        print(f"  - Name: {created['name']}")
    except Exception as e:
        print(f"CREATE FAILED: {str(e)}")
        return False

    # READ
    try:
        found = repo.find('w-test-agent-crud')
        assert found is not None
        print(f"\nREAD: Successfully found worker")
        print(f"  - ID: {found['worker_id']}")
        print(f"  - Name: {found['name']}")
        print(f"  - Tools: {found.get('enabled_tools', [])}")
    except Exception as e:
        print(f"READ FAILED: {str(e)}")
        return False

    # UPDATE
    try:
        updated = repo.update('w-test-agent-crud', {
            'name': 'Agent CRUD Test Worker (Updated)',
            'description': 'Modified by agent CRUD test'
        })
        print(f"\nUPDATE: Successfully updated worker")
        print(f"  - New name: {updated['name']}")
        print(f"  - New description: {updated['description']}")
    except Exception as e:
        print(f"UPDATE FAILED: {str(e)}")
        return False

    # DELETE
    try:
        deleted = repo.delete('w-test-agent-crud')
        assert deleted
        print(f"\nDELETE: Successfully deleted worker")

        # Verify deletion
        found_after = repo.find('w-test-agent-crud')
        assert found_after is None
        print(f"  - Verified: Worker no longer exists")
    except Exception as e:
        print(f"DELETE FAILED: {str(e)}")
        return False

    print(f"\nFinal count: {len(repo.list())} workers")
    return True


def test_user_crud():
    """Test UserRepository CRUD operations"""
    print("\n" + "="*60)
    print("TEST 2: UserRepository CRUD Operations")
    print("="*60)

    repo = UserRepository()

    # Backup original
    original_users = repo.list()
    print(f"Original count: {len(original_users)} users")

    # CREATE
    try:
        new_user = {
            'user_id': 'agent_test_user',
            'username': 'agent_test_user',
            'display_name': 'Agent Test User',
            'password_hash': 'test_hash',
            'role': 'user',
            'enabled': True,
            'worker_id': 'w-market-risk'
        }
        created = repo.create(new_user)
        print(f"\nCREATE: Successfully created user")
        print(f"  - ID: {created['user_id']}")
        print(f"  - Username: {created['username']}")
        print(f"  - Role: {created['role']}")
    except Exception as e:
        print(f"CREATE FAILED: {str(e)}")
        return False

    # READ
    try:
        found = repo.find('agent_test_user')
        assert found is not None
        print(f"\nREAD: Successfully found user")
        print(f"  - ID: {found['user_id']}")
        print(f"  - Username: {found['username']}")
        print(f"  - Display name: {found['display_name']}")
    except Exception as e:
        print(f"READ FAILED: {str(e)}")
        return False

    # UPDATE
    try:
        updated = repo.update('agent_test_user', {
            'display_name': 'Agent Test User (Updated)',
            'role': 'admin'
        })
        print(f"\nUPDATE: Successfully updated user")
        print(f"  - New display name: {updated['display_name']}")
        print(f"  - New role: {updated['role']}")
    except Exception as e:
        print(f"UPDATE FAILED: {str(e)}")
        return False

    # DELETE
    try:
        deleted = repo.delete('agent_test_user')
        assert deleted
        print(f"\nDELETE: Successfully deleted user")

        # Verify deletion
        found_after = repo.find('agent_test_user')
        assert found_after is None
        print(f"  - Verified: User no longer exists")
    except Exception as e:
        print(f"DELETE FAILED: {str(e)}")
        return False

    print(f"\nFinal count: {len(repo.list())} users")
    return True


def main():
    """Run all CRUD tests"""
    print("\n" + "#"*60)
    print("# REPOSITORY CRUD OPERATION TESTS")
    print("# Testing agent autonomy for worker and user management")
    print("#"*60)

    results = {
        'WorkerRepository CRUD': test_worker_crud(),
        'UserRepository CRUD': test_user_crud(),
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")

    all_passed = all(results.values())
    print("\n" + ("="*60))
    if all_passed:
        print("SUCCESS: Agent can independently manage workers and users!")
        print("Agent is fully autonomous - no MCP server required for CRUD.")
    else:
        print("FAILED: Some CRUD operations did not pass")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
