"""
Manual test script to demonstrate the multi-step deal evaluation pipeline
This script creates a test deal and walks through the evaluation pipeline
"""

import asyncio
import json

from app.db.session import SessionLocal
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal, User
from app.repositories.evaluation_repository import EvaluationRepository
from app.services.deal_evaluation_service import deal_evaluation_service


async def main():
    """Run manual test of evaluation pipeline"""
    db = SessionLocal()

    try:
        # Create test user
        print("Creating test user...")
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            full_name="Test User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created user: {user.username} (ID: {user.id})")

        # Create test deal
        print("\nCreating test deal...")
        deal = Deal(
            customer_name="John Doe",
            customer_email="john@example.com",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_year=2022,
            vehicle_mileage=15000,
            asking_price=25000.00,
        )
        db.add(deal)
        db.commit()
        db.refresh(deal)
        print(
            f"✓ Created deal: {deal.vehicle_year} {deal.vehicle_make} {deal.vehicle_model} (ID: {deal.id})"
        )

        # Create evaluation
        print("\n=== Starting Deal Evaluation Pipeline ===")
        repo = EvaluationRepository(db)
        evaluation = repo.create(
            user_id=user.id,
            deal_id=deal.id,
            status=EvaluationStatus.ANALYZING,
            current_step=PipelineStep.VEHICLE_CONDITION,
        )
        print(f"✓ Created evaluation (ID: {evaluation.id})")

        # Step 1: Vehicle Condition
        print("\n--- Step 1: Vehicle Condition ---")
        print("Processing without VIN/condition...")
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=None
        )
        db.refresh(evaluation)
        print(f"Status: {evaluation.status.value}")
        print(f"Questions: {result.get('questions', [])}")

        # Provide answers
        print("\nProviding answers...")
        answers = {
            "vin": "1HGBH41JXMN109186",
            "condition_description": "Excellent condition, well maintained",
        }
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=answers
        )
        db.refresh(evaluation)
        print(
            f"✓ Status: {evaluation.status.value}, Step: {evaluation.current_step.value}"
        )
        if result.get("assessment"):
            print(f"Assessment: {json.dumps(result['assessment'], indent=2)}")

        # Step 2: Price
        print("\n--- Step 2: Price Evaluation ---")
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=None
        )
        db.refresh(evaluation)
        print(
            f"✓ Status: {evaluation.status.value}, Step: {evaluation.current_step.value}"
        )
        if result.get("assessment"):
            assessment = result["assessment"]
            print(f"Fair Value: ${assessment.get('fair_value', 0):,.2f}")
            print(f"Score: {assessment.get('score', 0)}/10")

        # Step 3: Financing
        print("\n--- Step 3: Financing Evaluation ---")
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=None
        )
        db.refresh(evaluation)
        if result.get("questions"):
            print(f"Questions: {result['questions']}")
            # Provide financing answers
            financing_answers = {"financing_type": "cash"}
            result = await deal_evaluation_service.process_evaluation_step(
                db=db, evaluation_id=evaluation.id, user_answers=financing_answers
            )
            db.refresh(evaluation)
        print(
            f"✓ Status: {evaluation.status.value}, Step: {evaluation.current_step.value}"
        )
        if result.get("assessment"):
            print(f"Assessment: {json.dumps(result['assessment'], indent=2)}")

        # Step 4: Risk
        print("\n--- Step 4: Risk Assessment ---")
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=None
        )
        db.refresh(evaluation)
        print(
            f"✓ Status: {evaluation.status.value}, Step: {evaluation.current_step.value}"
        )
        if result.get("assessment"):
            assessment = result["assessment"]
            print(f"Risk Score: {assessment.get('risk_score', 0)}/10")
            print(f"Recommendation: {assessment.get('recommendation', 'N/A')}")

        # Step 5: Final
        print("\n--- Step 5: Final Evaluation ---")
        result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=None
        )
        db.refresh(evaluation)
        print(f"✓ Status: {evaluation.status.value}")
        if result.get("assessment"):
            assessment = result["assessment"]
            print(f"\n=== Final Results ===")
            print(f"Overall Score: {assessment.get('overall_score', 0)}/10")
            print(f"Recommendation: {assessment.get('recommendation', 'N/A')}")
            print(
                f"Estimated Total Cost: ${assessment.get('estimated_total_cost', 0):,.2f}"
            )
            print(f"Next Steps: {assessment.get('next_steps', [])}")

        # Show complete result
        print("\n=== Complete Evaluation Data ===")
        print(json.dumps(evaluation.result_json, indent=2))

        print("\n✓ Pipeline completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Deal Evaluation Pipeline - Manual Test")
    print("=" * 60)
    asyncio.run(main())
