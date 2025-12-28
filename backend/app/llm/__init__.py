"""
LLM module for OpenAI integration
"""

from app.llm.llm_client import (
    AgentRole,
    generate_structured_json,
    generate_text,
    llm_client,
)
from app.llm.prompts import get_prompt, list_prompts
from app.llm.schemas import (
    AddOnRecommendation,
    AffordabilityAssessment,
    CarSelectionItem,
    CarSelectionResponse,
    DealerFinancingOffer,
    DealEvaluation,
    FeeDetail,
    FinancingReport,
    LLMError,
    LLMRequest,
    LLMResponse,
    LoanOption,
    NegotiatedDeal,
    QAIssue,
    QAReport,
    SearchCriteria,
    VehicleConditionAssessment,
    VehicleInfo,
    VehicleReport,
)
from app.llm.agent_coordination import (
    AgentContext,
    AgentPipeline,
    DataEnricher,
    create_vehicle_research_pipeline,
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
    "AffordabilityAssessment",
    "NegotiatedDeal",
    "AddOnRecommendation",
    "FeeDetail",
    "DealerFinancingOffer",
    "QAReport",
    "QAIssue",
    # Agent coordination
    "AgentContext",
    "AgentPipeline",
    "DataEnricher",
    "create_vehicle_research_pipeline",
]
