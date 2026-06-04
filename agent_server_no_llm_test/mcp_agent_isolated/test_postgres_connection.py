"""
Test PostgreSQL connection
"""
import asyncio
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("=" * 60)
print("Testing PostgreSQL Connection")
print("=" * 60)

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env")
    print("\nAdd this to your .env:")
    print("DATABASE_URL=postgresql+psycopg://mcp_user:password@localhost:5432/mcp_onprem")
    exit(1)

print(f"\nConnection string: {DATABASE_URL}")

async def test_connection():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(DATABASE_URL, echo=False)

        async with engine.begin() as conn:
            result = await conn.execute(__import__('sqlalchemy').text("SELECT version();"))
            version = result.scalar()

        print("\n✅ Connection Successful!")
        print(f"PostgreSQL Version: {version}")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"\n❌ Connection Failed!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify DATABASE_URL in .env")
        print("3. Check username and password")
        print("4. Verify database exists: mcp_onprem")
        return False

if __name__ == '__main__':
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
