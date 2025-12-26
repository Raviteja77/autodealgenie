"""
Manual test script to verify MongoDB connection and operations
Run this to debug MongoDB data pipeline issues outside of pytest
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path in a portable way
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# ruff: noqa: E402
from app.core.config import settings
from app.db.mongodb import mongodb
from app.repositories.ai_response_repository import ai_response_repository
from app.repositories.search_history_repository import search_history_repository


async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("=" * 80)
    print("MongoDB Connection Test")
    print("=" * 80)

    # Test 1: Connect to MongoDB
    print("\n[Test 1] Connecting to MongoDB...")
    try:
        await mongodb.connect_db()
        print("✓ Successfully connected to MongoDB")
        print(f"✓ Using database: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return False

    # Test 2: Verify database and collection access
    print("\n[Test 2] Verifying database access...")
    try:
        db = mongodb.get_database()
        print(f"✓ Database instance obtained: {db.name}")

        collection = mongodb.get_collection("test_collection")
        print(f"✓ Collection instance obtained: {collection.name}")
    except Exception as e:
        print(f"✗ Failed to access database: {e}")
        return False

    # Test 3: Test search history repository with guaranteed cleanup
    print("\n[Test 3] Testing search history repository...")
    try:
        # Create a test search record
        search_id = await search_history_repository.create_search_record(
            user_id=999,  # Test user ID
            search_criteria={
                "make": "Honda",
                "model": "Civic",
                "budget_max": 25000,
            },
            result_count=10,
            top_vehicles=[
                {
                    "vin": "TEST123456789",
                    "make": "Honda",
                    "model": "Civic",
                    "year": 2023,
                    "price": 23000,
                }
            ],
        )
        print(f"✓ Created search history record with ID: {search_id}")

        # Retrieve the record
        history = await search_history_repository.get_user_history(user_id=999, limit=1)
        print(f"✓ Retrieved {len(history)} search history record(s)")
        if history:
            print(f"  - Record ID: {history[0].get('_id')}")
            print(f"  - Make: {history[0].get('search_criteria', {}).get('make')}")
            print(f"  - Timestamp: {history[0].get('timestamp')}")
    except Exception as e:
        print(f"✗ Search history test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Guaranteed cleanup
        try:
            deleted = await search_history_repository.delete_user_history(user_id=999)
            print(f"✓ Cleaned up {deleted} test record(s)")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup failed: {cleanup_error}")

    # Test 4: Test AI response repository with guaranteed cleanup
    print("\n[Test 4] Testing AI response repository...")
    try:
        # Create a test AI response record
        response_id = await ai_response_repository.create_response(
            feature="car_recommendation",
            user_id=999,
            deal_id=None,
            prompt_id="test_prompt",
            prompt_variables={"test": "data"},
            response_content="This is a test response",
            response_metadata={"score": 8.5, "confidence": 0.95},
            llm_used=True,
        )
        print(f"✓ Created AI response record with ID: {response_id}")

        # Retrieve by user ID
        responses = await ai_response_repository.get_by_user_id(user_id=999, limit=1)
        print(f"✓ Retrieved {len(responses)} AI response(s)")
        if responses:
            print(f"  - Record ID: {responses[0].get('_id')}")
            print(f"  - Feature: {responses[0].get('feature')}")
            print(f"  - Prompt ID: {responses[0].get('prompt_id')}")
            print(f"  - LLM Used: {responses[0].get('llm_used')}")

        # Retrieve by feature
        feature_responses = await ai_response_repository.get_by_feature(
            feature="car_recommendation", user_id=999, limit=10
        )
        print(f"✓ Retrieved {len(feature_responses)} response(s) for car_recommendation feature")

        # Get analytics
        analytics = await ai_response_repository.get_analytics(days=1)
        print(f"✓ Retrieved analytics: {analytics}")
    except Exception as e:
        print(f"✗ AI response test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Guaranteed cleanup
        try:
            collection = mongodb.get_collection("ai_responses")
            result = await collection.delete_many({"user_id": 999})
            print(f"✓ Cleaned up {result.deleted_count} test record(s)")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup failed: {cleanup_error}")

    # Test 5: List all collections
    print("\n[Test 5] Listing MongoDB collections...")
    try:
        db = mongodb.get_database()
        collections = await db.list_collection_names()
        print(f"✓ Found {len(collections)} collection(s):")
        for coll in collections:
            count = await db[coll].count_documents({})
            print(f"  - {coll}: {count} document(s)")
    except Exception as e:
        print(f"✗ Failed to list collections: {e}")
        return False

    # Test 6: Close connection
    print("\n[Test 6] Closing MongoDB connection...")
    try:
        await mongodb.close_db()
        print("✓ MongoDB connection closed successfully")
    except Exception as e:
        print(f"✗ Failed to close connection: {e}")
        return False

    print("\n" + "=" * 80)
    print("✓ All tests passed! MongoDB data pipeline is working correctly.")
    print("=" * 80)
    return True


if __name__ == "__main__":
    print(f"\nMongoDB URL: {settings.MONGODB_URL}")
    print(f"MongoDB Database: {settings.MONGODB_DB_NAME}\n")

    success = asyncio.run(test_mongodb_connection())
    sys.exit(0 if success else 1)
