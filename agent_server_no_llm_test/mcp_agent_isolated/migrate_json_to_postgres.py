"""
Migration script: JSON configs → PostgreSQL

Loads workers, users, and apikeys from JSON files and inserts into PostgreSQL.
Run this AFTER setting DATABASE_URL environment variable.
"""
import asyncio
import json
import pathlib
from pathlib import Path

# Database setup
from sajhamcpserver.sajha.db.engine import engine, AsyncSessionLocal
from sajhamcpserver.sajha.db.models import Worker, User, APIKey, Base


async def migrate_workers():
    """Load workers.json and insert into workers table."""
    workers_file = Path('sajhamcpserver/config/workers.json')

    if not workers_file.exists():
        print("❌ workers.json not found")
        return

    with open(workers_file, 'r') as f:
        data = json.load(f)

    workers_list = data.get('workers', [])

    async with AsyncSessionLocal() as session:
        for worker_data in workers_list:
            worker = Worker(
                worker_id=worker_data['worker_id'],
                name=worker_data['name'],
                description=worker_data.get('description'),
                system_prompt=worker_data.get('system_prompt'),
                enabled_tools=worker_data.get('enabled_tools', ['*']),
                domain_data_path=worker_data.get('domain_data_path'),
                verified_wf_path=worker_data.get('workflows_path'),
                my_workflows_path=worker_data.get('my_workflows_path'),
                templates_path=worker_data.get('templates_path'),
                my_data_path=worker_data.get('my_data_path'),
                common_data_path=worker_data.get('common_data_path'),
                connector_scope=worker_data.get('connector_scope', {}),
                enabled=worker_data.get('enabled', True),
            )
            session.add(worker)
            print(f"✅ Migrated worker: {worker.worker_id}")

        await session.commit()
        print(f"✅ Committed {len(workers_list)} workers to PostgreSQL")


async def migrate_users():
    """Load users.json and insert into users table."""
    users_file = Path('sajhamcpserver/config/users.json')

    if not users_file.exists():
        print("⚠️  users.json not found")
        return

    with open(users_file, 'r') as f:
        data = json.load(f)

    users_list = data.get('users', [])

    async with AsyncSessionLocal() as session:
        for user_data in users_list:
            user = User(
                user_id=user_data['user_id'],
                display_name=user_data.get('display_name', user_data['user_id']),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role', 'user'),
            )
            session.add(user)
            print(f"✅ Migrated user: {user.user_id}")

        await session.commit()
        print(f"✅ Committed {len(users_list)} users to PostgreSQL")


async def migrate_apikeys():
    """Load apikeys.json and insert into apikeys table."""
    apikeys_file = Path('sajhamcpserver/config/apikeys.json')

    if not apikeys_file.exists():
        print("⚠️  apikeys.json not found")
        return

    with open(apikeys_file, 'r') as f:
        data = json.load(f)

    apikeys_list = data.get('apikeys', [])

    async with AsyncSessionLocal() as session:
        for key_data in apikeys_list:
            apikey = APIKey(
                key_id=key_data['key_id'],
                key_secret=key_data.get('key_secret'),
                description=key_data.get('description'),
                rate_limit_rpm=key_data.get('rate_limit_rpm'),
                tool_filter=key_data.get('tool_filter', ['*']),
            )
            session.add(apikey)
            print(f"✅ Migrated API key: {apikey.key_id}")

        await session.commit()
        print(f"✅ Committed {len(apikeys_list)} API keys to PostgreSQL")


async def main():
    """Run all migrations."""
    print("=" * 60)
    print("MIGRATION: JSON Config → PostgreSQL")
    print("=" * 60)

    # Create tables
    print("\n[1/4] Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")

    # Migrate workers
    print("\n[2/4] Migrating workers...")
    await migrate_workers()

    # Migrate users
    print("\n[3/4] Migrating users...")
    await migrate_users()

    # Migrate API keys
    print("\n[4/4] Migrating API keys...")
    await migrate_apikeys()

    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify data in PostgreSQL")
    print("2. Keep JSON files as backup")
    print("3. Restart agent and SAJHA servers")
    print("4. Test worker/user/auth functionality")


if __name__ == '__main__':
    asyncio.run(main())
