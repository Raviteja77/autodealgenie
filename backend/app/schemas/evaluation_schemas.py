"""
Pydantic schemas for deal evaluation request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.evaluation import EvaluationStatus, PipelineStep


class EvaluationStepResult(BaseModel):
    """Schema for a single evaluation step result"""

    step: PipelineStep
    assessment: dict | None = Field(None, description="Step assessment data")
    questions: list[str] = Field(default_factory=list, description="Questions for user")
    completed: bool = Field(False, description="Whether this step is completed")


class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation"""

    deal_id: int = Field(..., description="Deal ID to evaluate")


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""

    id: int
    user_id: int
    deal_id: int
    status: EvaluationStatus
    current_step: PipelineStep
    result_json: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class EvaluationAnswerRequest(BaseModel):
    """Schema for submitting answers to evaluation questions"""

    answers: dict[str, str | int | float] = Field(
        ..., description="Answers to questions keyed by question identifier"
    )


class EvaluationInitiateRequest(BaseModel):
    """Schema for initiating or continuing an evaluation"""

    answers: dict[str, str | int | float] | None = Field(
        None, description="Optional answers to previous questions"
    )
