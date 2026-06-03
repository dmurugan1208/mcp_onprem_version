"""
Test all three repositories: Worker, User, APIKey
Verifies they load correctly and have data
"""
import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.repository import WorkerRepository, UserRepository, APIKeyRepository


def test_worker_repository():
    """Test WorkerRepository"""
    print("\n" + "="*60)
    print("TEST 1: WorkerRepository")
    print("="*60)

    repo = WorkerRepository()

    # Test list
    workers = repo.list()
    print(f"✅ Loaded {len(workers)} workers")

    if workers:
        first_worker = workers[0]
        print(f"   - Sample: {first_worker['worker_id']} ({first_worker['name']})")

    # Test find
    w_market = repo.find('w-market-risk')
    if w_market:
        print(f"✅ Found w-market-risk worker")
        print(f"   - Name: {w_market['name']}")
        print(f"   - Tools: {len(w_market.get('enabled_tools', []))} enabled")
        print(f"   - Mode: {w_market.get('agent_mode', 'single')}")
    else:
        print("❌ w-market-risk worker NOT found")

    return len(workers) > 0


def test_user_repository():
    """Test UserRepository"""
    print("\n" + "="*60)
    print("TEST 2: UserRepository")
    print("="*60)

    repo = UserRepository()

    # Test list
    users = repo.list()
    print(f"✅ Loaded {len(users)} users")

    if users:
        first_user = users[0]
        print(f"   - Sample: {first_user['user_id']} ({first_user.get('display_name', 'N/A')})")
        print(f"   - Role: {first_user.get('role', 'user')}")

    # Test find
    risk_agent = repo.find('risk_agent')
    if risk_agent:
        print(f"✅ Found risk_agent user")
        print(f"   - Display name: {risk_agent.get('display_name')}")
        print(f"   - Role: {risk_agent.get('role')}")
        print(f"   - Enabled: {risk_agent.get('enabled', True)}")
    else:
        print("⚠️  risk_agent user NOT found (might not exist)")

    # Test find_by_username
    if users and 'username' in users[0]:
        sample_username = users[0]['username']
        found = repo.find_by_username(sample_username)
        if found:
            print(f"✅ Found user by username: {sample_username}")

    # Test list_by_role
    admins = repo.list_by_role('super_admin')
    print(f"✅ Found {len(admins)} super_admin users")

    return len(users) > 0


def test_apikey_repository():
    """Test APIKeyRepository"""
    print("\n" + "="*60)
    print("TEST 3: APIKeyRepository")
    print("="*60)

    repo = APIKeyRepository()

    # Test list
    keys = repo.list()
    print(f"✅ Loaded {len(keys)} API keys")

    if keys:
        first_key = keys[0]
        print(f"   - Sample key_id: {first_key.get('key_id')}")
        print(f"   - Description: {first_key.get('description', 'N/A')}")

    # Test find
    if keys:
        key_id = keys[0].get('key_id')
        if key_id:
            found = repo.find(key_id)
            if found:
                print(f"✅ Found API key: {key_id}")
                print(f"   - Revoked: {found.get('revoked', False)}")
                print(f"   - Expires at: {found.get('expires_at', 'Never')}")

    # Test list_active
    active = repo.list_active()
    print(f"✅ Found {len(active)} active API keys (non-revoked, non-expired)")

    return len(keys) > 0


def test_agent_integration():
    """Test that agent_server can import and use repositories"""
    print("\n" + "="*60)
    print("TEST 4: Agent Server Integration")
    print("="*60)

    try:
        from agent_server import _worker_repo, _user_repo, _apikey_repo

        print(f"✅ agent_server imports successful")
        print(f"   - _worker_repo: {type(_worker_repo).__name__}")
        print(f"   - _user_repo: {type(_user_repo).__name__}")
        print(f"   - _apikey_repo: {type(_apikey_repo).__name__}")

        # Test that they work
        workers = _worker_repo.list()
        users = _user_repo.list()
        keys = _apikey_repo.list()

        print(f"✅ All repos are instantiated and working")
        print(f"   - Workers: {len(workers)}")
        print(f"   - Users: {len(users)}")
        print(f"   - API Keys: {len(keys)}")

        return True
    except Exception as e:
        print(f"❌ Agent integration failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# REPOSITORY VERIFICATION TESTS")
    print("#"*60)

    results = {
        'WorkerRepository': test_worker_repository(),
        'UserRepository': test_user_repository(),
        'APIKeyRepository': test_apikey_repository(),
        'Agent Integration': test_agent_integration(),
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(results.values())
    print("\n" + ("="*60))
    if all_passed:
        print("✅ ALL TESTS PASSED - Repositories are working!")
    else:
        print("❌ SOME TESTS FAILED - Check output above")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
