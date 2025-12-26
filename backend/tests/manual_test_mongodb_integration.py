"""
Manual integration test for MongoDB operations via API endpoints
Tests the complete data flow from endpoint to MongoDB
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ruff: noqa: E402
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.mongodb import mongodb
from app.db.session import Base
from app.repositories.search_history_repository import search_history_repository

# Create test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


async def setup_mongodb():
    """Initialize MongoDB for testing"""
    await mongodb.connect_db()
    print("✓ MongoDB connected for integration test")


async def cleanup_mongodb():
    """Clean up test data and close MongoDB"""
    # Clean up test data
    collection = mongodb.get_collection("search_history")
    result = await collection.delete_many({"search_criteria.test_marker": "integration_test"})
    print(f"✓ Cleaned up {result.deleted_count} test search history records")

    collection = mongodb.get_collection("ai_responses")
    result = await collection.delete_many({"prompt_variables.test_marker": "integration_test"})
    print(f"✓ Cleaned up {result.deleted_count} test AI response records")

    await mongodb.close_db()
    print("✓ MongoDB closed")


async def test_search_history_via_service():
    """Test search history creation via car recommendation service"""
    print("\n" + "=" * 80)
    print("Integration Test: Search History via Service")
    print("=" * 80)

    # Import here to avoid circular dependencies
    from app.services.car_recommendation_service import car_recommendation_service

    # Test 1: Check if MarketCheck API is available
    print("\n[Test 1] Creating search via recommendation service...")

    # Skip external API call if not configured
    api_key = getattr(settings, "MARKET_CHECK_API_KEY", None)
    if not api_key:
        print(
            "⚠ MarketCheck API not configured. Skipping external API call in "
            "test_search_history_via_service."
        )
        print("  Note: This test only runs fully when the external API is available.")
        return True

    try:
        # Call the recommendation service
        result = await car_recommendation_service.search_and_recommend(
            make="Honda",
            model="Civic",
            budget_min=20000,
            budget_max=30000,
            user_priorities="Best value for money",
            user_id=888,  # Test user ID
            max_results=5,
        )
        print(f"✓ Search completed with {result.get('total_found', 0)} results")

        # Verify data was stored in MongoDB
        history = await search_history_repository.get_user_history(user_id=888, limit=10)
        print(f"✓ Found {len(history)} search history records for user 888")

        if history:
            latest = history[0]
            print(f"  - Latest search: {latest.get('search_criteria', {}).get('make')}")
            print(f"  - Result count: {latest.get('result_count')}")
            print(f"  - Timestamp: {latest.get('timestamp')}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise
    finally:
        # Guaranteed cleanup
        try:
            deleted = await search_history_repository.delete_user_history(user_id=888)
            print(f"✓ Cleaned up {deleted} test records")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup failed: {cleanup_error}")

    print("\n✓ Integration test passed!")
    return True


async def test_ai_response_logging():
    """Test AI response logging via negotiation service"""
    print("\n" + "=" * 80)
    print("Integration Test: AI Response Logging")
    print("=" * 80)

    from app.repositories.ai_response_repository import ai_response_repository

    print("\n[Test 1] Creating AI response via repository...")
    try:
        # Create a test AI response
        response_id = await ai_response_repository.create_response(
            feature="negotiation",
            user_id=888,
            deal_id=123,
            prompt_id="test_integration",
            prompt_variables={"test_marker": "integration_test"},
            response_content="Test AI response for integration",
            response_metadata={"score": 9.0},
            llm_used=True,
        )
        print(f"✓ Created AI response with ID: {response_id}")

        # Retrieve and verify
        responses = await ai_response_repository.get_by_user_id(user_id=888, limit=10)
        print(f"✓ Retrieved {len(responses)} AI responses for user 888")

        if responses:
            latest = responses[0]
            print(f"  - Feature: {latest.get('feature')}")
            print(f"  - Prompt ID: {latest.get('prompt_id')}")
            print(f"  - LLM Used: {latest.get('llm_used')}")
    except Exception as e:
        print(f"✗ AI response test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        # Guaranteed cleanup - NOTE: We intentionally use the raw MongoDB collection here
        # because the AI response repository does not currently expose a bulk-delete/cleanup
        # method. This direct access is limited to this integration test and is scoped to
        # a known test user_id (888) to avoid interfering with non-test data.
        try:
            collection = mongodb.get_collection("ai_responses")
            result = await collection.delete_many({"user_id": 888})
            print(f"✓ Cleaned up {result.deleted_count} test records")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup failed: {cleanup_error}")

    print("\n✓ Integration test passed!")
    return True


async def main():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("MongoDB Integration Tests")
    print("=" * 80)

    try:
        # Setup
        await setup_mongodb()

        # Run tests
        await test_ai_response_logging()
        await test_search_history_via_service()

        # Cleanup
        await cleanup_mongodb()

        print("\n" + "=" * 80)
        print("✓ All integration tests passed!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n✗ Integration tests failed: {e}")
        import traceback

        traceback.print_exc()

        # Try to cleanup even on failure; log but don't mask the original error
        try:
            await cleanup_mongodb()
        except Exception as cleanup_error:
            print(f"Warning: failed to cleanup MongoDB after test failure: {cleanup_error}")

        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
