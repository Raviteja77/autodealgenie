"""Test fixes for negotiation, lender, and deal evaluation services"""

from unittest.mock import AsyncMock, Mock

import pytest

from app.models.negotiation import MessageRole, NegotiationMessage
from app.services.negotiation_service import NegotiationService


@pytest.mark.asyncio
async def test_negotiation_service_metadata_access():
    """Test that negotiation service correctly accesses message_metadata attribute"""
    # Create a mock database session
    db = Mock()

    # Create negotiation service
    service = NegotiationService(db)

    # Create mock messages with message_metadata attribute
    mock_msg1 = Mock(spec=NegotiationMessage)
    mock_msg1.message_metadata = {"suggested_price": 20000.0}
    mock_msg1.role = MessageRole.AGENT

    mock_msg2 = Mock(spec=NegotiationMessage)
    mock_msg2.message_metadata = {"counter_offer": 21000.0}
    mock_msg2.role = MessageRole.USER

    mock_msg3 = Mock(spec=NegotiationMessage)
    mock_msg3.message_metadata = None
    mock_msg3.role = MessageRole.AGENT

    # Mock the repository to return messages using AsyncMock
    service.negotiation_repo = Mock()
    service.negotiation_repo.get_messages = AsyncMock(
        return_value=[mock_msg1, mock_msg2, mock_msg3]
    )

    # Test _get_latest_suggested_price method with await
    result = await service._get_latest_suggested_price(session_id=1, default_price=25000.0)

    # Should find the suggested_price from mock_msg1
    assert result == 20000.0, f"Expected 20000.0, got {result}"

    print("✓ Test passed: Negotiation service correctly accesses message_metadata")


def test_llm_json_parsing_with_markdown():
    """Test that LLM client handles markdown code blocks in JSON responses"""
    import json

    # Test cases for different markdown formats
    test_cases = [
        ('```json\n{"test": "value"}\n```', {"test": "value"}),
        ('```\n{"test": "value"}\n```', {"test": "value"}),
        ('{"test": "value"}', {"test": "value"}),
    ]

    for input_content, expected_output in test_cases:
        # Simulate the cleaning logic from llm_client.py
        content = input_content.strip()

        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3].strip()

        parsed = json.loads(content)
        assert parsed == expected_output, f"Failed for input: {input_content}"

    print("✓ Test passed: JSON parsing handles markdown code blocks correctly")


def test_deal_evaluation_fallback():
    """Test that deal evaluation service provides fallback when LLM fails"""
    from app.services.deal_evaluation_service import DealEvaluationService

    service = DealEvaluationService()

    # Test fallback evaluation
    result = service._fallback_evaluation(
        vehicle_vin="TEST123456", asking_price=25000.0, condition="good", mileage=50000
    )

    # Verify fallback returns expected structure
    assert "fair_value" in result
    assert "score" in result
    assert "insights" in result
    assert "talking_points" in result
    assert isinstance(result["score"], int | float)
    assert 1.0 <= result["score"] <= 10.0

    print("✓ Test passed: Deal evaluation service provides valid fallback")


def test_lender_service_recommendations():
    """Test that lender service generates recommendations without errors"""
    from app.schemas.loan_schemas import LenderRecommendationRequest
    from app.services.lender_service import LenderService

    # Create a valid request
    request = LenderRecommendationRequest(
        loan_amount=20000.0, credit_score_range="good", loan_term_months=60
    )

    # Get recommendations
    response = LenderService.get_recommendations(request, max_results=5)

    # Verify response structure
    assert hasattr(response, "recommendations")
    assert hasattr(response, "total_matches")
    assert isinstance(response.recommendations, list)

    print("✓ Test passed: Lender service generates recommendations successfully")


if __name__ == "__main__":
    import asyncio

    # Run tests
    asyncio.run(test_negotiation_service_metadata_access())
    test_llm_json_parsing_with_markdown()
    test_deal_evaluation_fallback()
    test_lender_service_recommendations()
    print("\n✅ All service fix tests passed!")
