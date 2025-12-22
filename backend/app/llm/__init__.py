"""
LLM module for OpenAI integration
"""

from app.llm.llm_client import AgentRole, generate_structured_json, generate_text, llm_client
from app.llm.prompts import get_prompt, list_prompts
from app.llm.schemas import (
    AddOn,
    CarSelectionItem,
    CarSelectionResponse,
    DealerFinancing,
    DealEvaluation,
    Fee,
    FinancingReport,
    LLMError,
    LLMRequest,
    LLMResponse,
    LoanOption,
    NegotiatedDeal,
    QAReport,
    SearchCriteria,
    VehicleConditionAssessment,
    VehicleInfo,
    VehicleReport,
)

__all__ = [
    "llm_client",
    "generate_structured_json",
    "generate_text",
    "get_prompt",
    "list_prompts",
    "AgentRole",
    "LLMRequest",
    "LLMResponse",
    "LLMError",
    "CarSelectionItem",
    "CarSelectionResponse",
    "DealEvaluation",
    "VehicleConditionAssessment",
    "VehicleReport",
    "VehicleInfo",
    "SearchCriteria",
    "FinancingReport",
    "LoanOption",
    "NegotiatedDeal",
    "AddOn",
    "Fee",
    "DealerFinancing",
    "QAReport",
]
