"""
Deal Evaluation Service Package

This package provides modular deal evaluation functionality following the orchestrator pattern.
"""

# Note: DealEvaluationService will be imported from .core when needed
# The singleton instance is created at module level to avoid circular import issues

__all__ = ["DealEvaluationService", "deal_evaluation_service"]


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name == "DealEvaluationService":
        from app.services.evaluation.core import DealEvaluationService

        return DealEvaluationService
    elif name == "deal_evaluation_service":
        from app.services.evaluation.core import DealEvaluationService

        # Create singleton instance
        global _singleton_instance
        if "_singleton_instance" not in globals():
            _singleton_instance = DealEvaluationService()
        return _singleton_instance
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
