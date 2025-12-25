"""
Repository pattern for DealEvaluation operations
"""

from sqlalchemy.orm import Session

from app.models.evaluation import DealEvaluation, EvaluationStatus, PipelineStep


class EvaluationRepository:
    """Repository for DealEvaluation database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        deal_id: int,
        status: EvaluationStatus,
        current_step: PipelineStep,
    ) -> DealEvaluation:
        """Create a new deal evaluation"""
        evaluation = DealEvaluation(
            user_id=user_id, deal_id=deal_id, status=status, current_step=current_step
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def get(self, evaluation_id: int) -> DealEvaluation | None:
        """Get an evaluation by ID"""
        return self.db.query(DealEvaluation).filter(DealEvaluation.id == evaluation_id).first()

    def get_by_deal(self, deal_id: int) -> list[DealEvaluation]:
        """Get all evaluations for a deal"""
        return self.db.query(DealEvaluation).filter(DealEvaluation.deal_id == deal_id).all()

    def get_latest_by_deal(self, deal_id: int) -> DealEvaluation | None:
        """Get the most recent evaluation for a deal"""
        return (
            self.db.query(DealEvaluation)
            .filter(DealEvaluation.deal_id == deal_id)
            .order_by(DealEvaluation.created_at.desc())
            .first()
        )

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[DealEvaluation]:
        """Get all evaluations for a user with pagination"""
        return (
            self.db.query(DealEvaluation)
            .filter(DealEvaluation.user_id == user_id)
            .order_by(DealEvaluation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(self, evaluation_id: int, status: EvaluationStatus) -> DealEvaluation | None:
        """Update evaluation status"""
        evaluation = self.get(evaluation_id)
        if not evaluation:
            return None

        evaluation.status = status
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def update_step(self, evaluation_id: int, current_step: PipelineStep) -> DealEvaluation | None:
        """Update evaluation current step"""
        evaluation = self.get(evaluation_id)
        if not evaluation:
            return None

        evaluation.current_step = current_step
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def update_result(
        self,
        evaluation_id: int,
        result_json: dict,
        status: EvaluationStatus | None = None,
    ) -> DealEvaluation | None:
        """Update evaluation result JSON and optionally status"""
        evaluation = self.get(evaluation_id)
        if not evaluation:
            return None

        evaluation.result_json = result_json
        if status:
            evaluation.status = status
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def advance_step(
        self, evaluation_id: int, next_step: PipelineStep, step_result: dict
    ) -> DealEvaluation | None:
        """Advance to next step and update results"""
        evaluation = self.get(evaluation_id)
        if not evaluation:
            return None

        # Update result_json with new step data
        result_json = evaluation.result_json or {}
        result_json[evaluation.current_step.value] = step_result

        evaluation.current_step = next_step
        evaluation.result_json = result_json
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def delete(self, evaluation_id: int) -> bool:
        """Delete an evaluation"""
        evaluation = self.get(evaluation_id)
        if not evaluation:
            return False

        self.db.delete(evaluation)
        self.db.commit()
        return True
