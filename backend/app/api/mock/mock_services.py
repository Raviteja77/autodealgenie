"""
Mock implementations for essential services
Provides mock endpoints for Market Check API, LLM, Negotiation, and Deal Evaluation services
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


# ============================================================================
# Mock Data
# ============================================================================

MOCK_VEHICLES = [
    {
        "vin": "1HGCM82633A123456",
        "make": "Honda",
        "model": "Accord",
        "year": 2023,
        "trim": "EX-L",
        "mileage": 15000,
        "price": 28500,
        "msrp": 32000,
        "location": "Los Angeles, CA",
        "dealer_name": "Honda of Downtown",
        "dealer_contact": "123 Main St, Los Angeles, CA 90001 (555) 123-4567",
        "photo_links": [
            "https://images.unsplash.com/photo-1590362891991-f776e747a588?w=800",
            "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=800",
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800",
        ],
        "vdp_url": "https://example.com/vehicle/123456",
        "exterior_color": "Modern Steel Metallic",
        "interior_color": "Black",
        "drivetrain": "FWD",
        "transmission": "Automatic",
        "engine": "1.5L Turbo",
        "fuel_type": "Gasoline",
        "carfax_1_owner": True,
        "carfax_clean_title": True,
        "inventory_type": "used",
        "days_on_market": 12,
    },
    {
        "vin": "5YJ3E1EA3KF123789",
        "make": "Tesla",
        "model": "Model 3",
        "year": 2022,
        "trim": "Long Range",
        "mileage": 8500,
        "price": 42000,
        "msrp": 48000,
        "location": "San Francisco, CA",
        "dealer_name": "Tesla Direct",
        "dealer_contact": "456 Tech Blvd, San Francisco, CA 94103 (555) 987-6543",
        "photo_links": [
            "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800",
            "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800",
        ],
        "vdp_url": "https://example.com/vehicle/789012",
        "exterior_color": "Pearl White Multi-Coat",
        "interior_color": "White",
        "drivetrain": "AWD",
        "transmission": "Single-Speed",
        "engine": "Electric",
        "fuel_type": "Electric",
        "carfax_1_owner": True,
        "carfax_clean_title": True,
        "inventory_type": "used",
        "days_on_market": 5,
    },
    {
        "vin": "1C4RJFBG8KC123456",
        "make": "Jeep",
        "model": "Grand Cherokee",
        "year": 2023,
        "trim": "Limited",
        "mileage": 22000,
        "price": 38900,
        "msrp": 45000,
        "location": "Phoenix, AZ",
        "dealer_name": "Desert Jeep Center",
        "dealer_contact": "789 Desert Dr, Phoenix, AZ 85001 (555) 456-7890",
        "photo_links": [
            "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800",
            "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800",
        ],
        "vdp_url": "https://example.com/vehicle/345678",
        "exterior_color": "Diamond Black Crystal",
        "interior_color": "Black/Ski Grey",
        "drivetrain": "4WD",
        "transmission": "8-Speed Automatic",
        "engine": "3.6L V6",
        "fuel_type": "Gasoline",
        "carfax_1_owner": False,
        "carfax_clean_title": True,
        "inventory_type": "certified",
        "days_on_market": 18,
    },
    {
        "vin": "3VW2B7AJ6KM123456",
        "make": "Volkswagen",
        "model": "Jetta",
        "year": 2023,
        "trim": "SEL Premium",
        "mileage": 12000,
        "price": 24500,
        "msrp": 28000,
        "location": "Austin, TX",
        "dealer_name": "VW of Austin",
        "dealer_contact": "321 Cedar St, Austin, TX 78701 (555) 234-5678",
        "photo_links": [
            "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800",
        ],
        "vdp_url": "https://example.com/vehicle/901234",
        "exterior_color": "Pure White",
        "interior_color": "Titan Black",
        "drivetrain": "FWD",
        "transmission": "8-Speed Automatic",
        "engine": "1.4L Turbo",
        "fuel_type": "Gasoline",
        "carfax_1_owner": True,
        "carfax_clean_title": True,
        "inventory_type": "used",
        "days_on_market": 8,
    },
    {
        "vin": "5UXCR6C01L9B12345",
        "make": "BMW",
        "model": "X5",
        "year": 2022,
        "trim": "xDrive40i",
        "mileage": 18000,
        "price": 52000,
        "msrp": 62000,
        "location": "Miami, FL",
        "dealer_name": "BMW of Miami",
        "dealer_contact": "555 Ocean Dr, Miami, FL 33139 (555) 345-6789",
        "photo_links": [
            "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
            "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=800",
        ],
        "vdp_url": "https://example.com/vehicle/567890",
        "exterior_color": "Alpine White",
        "interior_color": "Black Vernasca Leather",
        "drivetrain": "AWD",
        "transmission": "8-Speed Automatic",
        "engine": "3.0L Inline-6 Turbo",
        "fuel_type": "Gasoline",
        "carfax_1_owner": True,
        "carfax_clean_title": True,
        "inventory_type": "certified",
        "days_on_market": 15,
    },
]


# ============================================================================
# Market Check Mock Endpoints
# ============================================================================


@router.post("/search")
async def mock_car_search(request_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Mock endpoint for car search (MarketCheck API)
    Returns a filtered list of mock vehicles based on search criteria
    """
    if request_data is None:
        request_data = {}

    # Extract search parameters
    make = request_data.get("make", "").lower() if request_data.get("make") else None
    model = request_data.get("model", "").lower() if request_data.get("model") else None
    budget_min = request_data.get("budget_min") or request_data.get("min_price")
    budget_max = request_data.get("budget_max") or request_data.get("max_price")
    year_min = request_data.get("year_min") or request_data.get("min_year")
    year_max = request_data.get("year_max") or request_data.get("max_year")

    # Filter vehicles
    filtered_vehicles = []
    for vehicle in MOCK_VEHICLES:
        # Apply filters
        if make and vehicle["make"].lower() != make:
            continue
        if model and vehicle["model"].lower() != model:
            continue
        if budget_min and vehicle["price"] < budget_min:
            continue
        if budget_max and vehicle["price"] > budget_max:
            continue
        if year_min and vehicle["year"] < year_min:
            continue
        if year_max and vehicle["year"] > year_max:
            continue

        filtered_vehicles.append(vehicle)

    # Add recommendation metadata to match expected response format
    for i, vehicle in enumerate(filtered_vehicles):
        vehicle["recommendation_score"] = 9.0 - (i * 0.5)  # Decreasing scores
        vehicle["highlights"] = [
            f"Great value at ${vehicle['price']:,}",
            f"Low mileage: {vehicle['mileage']:,} miles",
            f"Clean title and well-maintained",
        ]
        vehicle["recommendation_summary"] = (
            f"Excellent choice! This {vehicle['year']} {vehicle['make']} {vehicle['model']} "
            f"offers great value with {vehicle['mileage']:,} miles and modern features."
        )

    return {
        "search_criteria": {
            "make": make,
            "model": model,
            "price_min": budget_min,
            "price_max": budget_max,
            "year_min": year_min,
            "year_max": year_max,
        },
        "top_vehicles": filtered_vehicles[:5],  # Return top 5
        "total_found": len(filtered_vehicles),
        "total_analyzed": len(MOCK_VEHICLES),
        "message": f"Found {len(filtered_vehicles)} vehicles matching your criteria",
    }


# ============================================================================
# LLM Mock Endpoints
# ============================================================================


@router.post("/generate")
async def mock_llm_generate(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for LLM text generation
    Returns mock responses based on prompt_id
    """
    prompt_id = request_data.get("prompt_id", "")
    variables = request_data.get("variables", {})

    # Generate mock response based on prompt type
    if "negotiation" in prompt_id:
        content = generate_mock_negotiation_response(variables)
    elif "evaluation" in prompt_id:
        content = generate_mock_evaluation_response(variables)
    elif "recommendation" in prompt_id:
        content = generate_mock_recommendation_response(variables)
    else:
        content = "This is a mock LLM response for development purposes."

    return {
        "content": content,
        "prompt_id": prompt_id,
        "model": "mock-gpt-4",
        "tokens_used": 150,
    }


@router.post("/generate-structured")
async def mock_llm_generate_structured(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for LLM structured JSON generation
    Returns mock structured data based on prompt_id
    """
    prompt_id = request_data.get("prompt_id", "")
    variables = request_data.get("variables", {})

    # Generate mock structured response based on prompt type
    if "evaluation" in prompt_id:
        content = {
            "fair_value": float(variables.get("asking_price", 30000)) * 0.95,
            "score": 8.5,
            "insights": [
                "Vehicle is priced competitively below market average",
                "Clean title and single owner history adds value",
                "Recent service records show excellent maintenance",
                "Low mileage for the model year increases appeal",
            ],
            "talking_points": [
                "Emphasize the below-market pricing as a fair deal",
                "Highlight the clean maintenance history",
                "Note that similar vehicles sell quickly at this price point",
                "Consider offering asking price with extended warranty",
            ],
        }
    elif "selection" in prompt_id or "recommendation" in prompt_id:
        content = {
            "recommendations": [
                {
                    "index": 0,
                    "score": 9.2,
                    "highlights": [
                        "Excellent value for money",
                        "Low mileage and clean history",
                        "Highly reliable model",
                    ],
                    "summary": "Best overall choice combining value, reliability, and condition",
                },
                {
                    "index": 1,
                    "score": 8.8,
                    "highlights": [
                        "Premium features included",
                        "Recent model year",
                        "Great fuel efficiency",
                    ],
                    "summary": "Excellent option with modern technology and efficiency",
                },
            ]
        }
    else:
        content = {"message": "Mock structured response", "status": "success"}

    return {
        "content": content,
        "prompt_id": prompt_id,
        "model": "mock-gpt-4",
        "tokens_used": 200,
    }


def generate_mock_negotiation_response(variables: dict[str, Any]) -> str:
    """Generate mock negotiation text"""
    round_num = variables.get("round_number", 1)
    user_offer = variables.get("counter_offer")
    asking_price = variables.get("asking_price", 30000)

    if round_num == 1:
        return (
            f"Thank you for your interest! The asking price for this vehicle is ${asking_price:,}. "
            "This is a competitive price based on current market conditions and the vehicle's excellent condition. "
            "What price range were you considering?"
        )
    elif user_offer:
        suggested = (asking_price + user_offer) / 2
        return (
            f"I appreciate your offer of ${user_offer:,}. While I understand your perspective, "
            f"given the vehicle's condition and market value, I could meet you at ${suggested:,.0f}. "
            "This represents a fair compromise that reflects the true value of this vehicle."
        )
    else:
        return (
            "I understand you'd like to negotiate. The current asking price reflects the "
            "vehicle's excellent condition and market value. What specific price did you have in mind?"
        )


def generate_mock_evaluation_response(variables: dict[str, Any]) -> str:
    """Generate mock evaluation text"""
    make = variables.get("make", "this vehicle")
    model = variables.get("model", "")
    year = variables.get("year", "")
    price = variables.get("asking_price", 0)

    vehicle_desc = f"{year} {make} {model}" if year and model else make
    fair_value = price * 0.95

    return (
        f"Based on current market data, the {vehicle_desc} has a fair market value "
        f"of approximately ${fair_value:,.0f}. The asking price of ${price:,} represents "
        "a reasonable deal considering the vehicle's condition, mileage, and market trends."
    )


def generate_mock_recommendation_response(variables: dict[str, Any]) -> str:
    """Generate mock recommendation text"""
    return (
        "Based on your preferences and budget, I've identified several excellent options. "
        "These vehicles offer the best combination of value, reliability, and features "
        "that match your criteria. Each has been thoroughly evaluated for condition and pricing."
    )


# ============================================================================
# Negotiation Mock Endpoints
# ============================================================================


MOCK_NEGOTIATIONS = {}
NEGOTIATION_ID_COUNTER = 1000


@router.post("/create")
async def mock_create_negotiation(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for creating a negotiation session
    """
    global NEGOTIATION_ID_COUNTER

    deal_id = request_data.get("deal_id")
    user_target_price = request_data.get("user_target_price")
    strategy = request_data.get("strategy")

    if not deal_id or not user_target_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="deal_id and user_target_price are required",
        )

    session_id = NEGOTIATION_ID_COUNTER
    NEGOTIATION_ID_COUNTER += 1

    # Create mock session
    session = {
        "session_id": session_id,
        "deal_id": deal_id,
        "status": "active",
        "current_round": 1,
        "user_target_price": user_target_price,
        "strategy": strategy,
        "asking_price": 30000,  # Mock asking price
    }

    MOCK_NEGOTIATIONS[session_id] = session

    # Generate initial agent response
    agent_message = (
        f"Welcome! I see you're interested in this vehicle. The current asking price is $30,000. "
        f"I understand you're targeting ${user_target_price:,.0f}. Let's see if we can work "
        "together to find a price that works for everyone."
    )

    return {
        "session_id": session_id,
        "status": "active",
        "current_round": 1,
        "agent_message": agent_message,
        "metadata": {
            "suggested_price": 29000,
            "asking_price": 30000,
            "user_target": user_target_price,
        },
    }


@router.post("/{session_id}/next")
async def mock_process_next_round(session_id: int, request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for processing the next negotiation round
    """
    if session_id not in MOCK_NEGOTIATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session = MOCK_NEGOTIATIONS[session_id]
    user_action = request_data.get("user_action")
    counter_offer = request_data.get("counter_offer")

    current_round = session["current_round"]
    asking_price = session["asking_price"]

    # Update session
    session["current_round"] = current_round + 1

    # Generate response based on action
    if user_action == "confirm":
        session["status"] = "completed"
        agent_message = (
            "Excellent! I'm glad we could reach an agreement. Let's proceed with finalizing "
            "the paperwork. Congratulations on your purchase!"
        )
        suggested_price = asking_price
    elif user_action == "reject":
        session["status"] = "cancelled"
        agent_message = (
            "I understand this doesn't meet your needs. Thank you for your time, and please "
            "feel free to reach out if your situation changes!"
        )
        suggested_price = asking_price
    else:  # counter
        if not counter_offer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="counter_offer is required for counter action",
            )

        # Calculate a middle ground
        suggested_price = (asking_price + counter_offer) / 2

        # Update asking price to reflect negotiation progress
        session["asking_price"] = suggested_price

        agent_message = (
            f"I appreciate your offer of ${counter_offer:,.0f}. Let me see what I can do. "
            f"How about we meet in the middle at ${suggested_price:,.0f}? This reflects "
            "the vehicle's value while being fair to both parties."
        )

    return {
        "session_id": session_id,
        "status": session["status"],
        "current_round": session["current_round"],
        "agent_message": agent_message,
        "metadata": {
            "suggested_price": suggested_price,
            "asking_price": session["asking_price"],
            "user_action": user_action,
        },
    }


@router.get("/{session_id}")
async def mock_get_negotiation(session_id: int) -> dict[str, Any]:
    """
    Mock endpoint for retrieving a negotiation session
    """
    if session_id not in MOCK_NEGOTIATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session = MOCK_NEGOTIATIONS[session_id]
    return {
        "session_id": session_id,
        "deal_id": session["deal_id"],
        "status": session["status"],
        "current_round": session["current_round"],
        "strategy": session.get("strategy"),
        "messages": [
            {
                "role": "agent",
                "content": "Welcome! Let's discuss the pricing for this vehicle.",
                "round_number": 1,
            }
        ],
    }


# ============================================================================
# Deal Evaluation Mock Endpoints
# ============================================================================


@router.post("/evaluate")
async def mock_evaluate_deal(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for deal evaluation
    Returns mock evaluation data
    """
    vin = request_data.get("vehicle_vin") or request_data.get("vin")
    asking_price = request_data.get("asking_price", 30000)
    condition = request_data.get("condition", "good")
    mileage = request_data.get("mileage", 50000)

    # Generate mock evaluation based on inputs
    # Fair value is typically 95% of asking price in our mock
    fair_value = asking_price * 0.95

    # Score based on condition
    condition_scores = {"excellent": 9.5, "good": 8.0, "fair": 6.5, "poor": 4.0}
    base_score = condition_scores.get(condition.lower(), 7.0)

    # Adjust score based on mileage (lower mileage = higher score)
    if mileage < 30000:
        mileage_adjustment = 1.0
    elif mileage < 60000:
        mileage_adjustment = 0.5
    elif mileage < 100000:
        mileage_adjustment = 0
    else:
        mileage_adjustment = -0.5

    final_score = max(1.0, min(10.0, base_score + mileage_adjustment))

    return {
        "vin": vin,
        "fair_value": fair_value,
        "score": final_score,
        "insights": [
            f"Vehicle is priced at ${asking_price:,} with estimated fair value of ${fair_value:,.0f}",
            f"Condition reported as '{condition}' which is {condition.lower()} for this model",
            f"Mileage of {mileage:,} miles is {'low' if mileage < 50000 else 'average'} for the year",
            "Market data suggests steady demand for this model",
            "Comparable vehicles typically sell within 2-3 weeks",
        ],
        "talking_points": [
            f"The asking price is {'competitive' if asking_price <= fair_value else 'slightly above'} market value",
            "Consider negotiating based on any needed repairs or maintenance",
            "Vehicle history report should be reviewed before finalizing",
            f"Similar vehicles with {condition} condition sell in this price range",
            "Request a pre-purchase inspection for peace of mind",
        ],
        "asking_price": asking_price,
        "condition": condition,
        "mileage": mileage,
    }


# ============================================================================
# Evaluation Pipeline Mock Endpoints
# ============================================================================

# Store evaluation state in memory
MOCK_EVALUATIONS = {}
EVALUATION_ID_COUNTER = 5000


@router.post("/evaluation/pipeline/{deal_id}/evaluation")
async def mock_start_evaluation(deal_id: int, request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Mock endpoint for starting evaluation pipeline
    Simulates POST /api/v1/deals/{deal_id}/evaluation
    """
    global EVALUATION_ID_COUNTER

    answers = request_data.get("answers", {})
    evaluation_id = EVALUATION_ID_COUNTER
    EVALUATION_ID_COUNTER += 1

    # Check if VIN was provided
    if answers and "vin" in answers:
        # Start with condition assessment (no questions needed)
        step_result = {
            "assessment": {
                "condition_score": 8.5,
                "condition_notes": [
                    "Vehicle appears well-maintained based on reported condition",
                    "Mileage is reasonable for the year",
                    "No major concerns identified in initial assessment",
                ],
                "recommended_inspection": True,
            },
            "completed": True,
        }
        status = "analyzing"
        current_step = "vehicle_condition"
        result_json = {
            "user_inputs": answers,
            "vehicle_condition": step_result,
        }
    else:
        # Ask for VIN and condition
        step_result = {
            "questions": [
                "What is the Vehicle Identification Number (VIN)?",
                "Please describe the vehicle's condition (e.g., excellent, good, fair, poor)",
            ],
            "required_fields": ["vin", "condition_description"],
        }
        status = "awaiting_input"
        current_step = "vehicle_condition"
        result_json = {"user_inputs": answers} if answers else None

    # Store evaluation state
    MOCK_EVALUATIONS[evaluation_id] = {
        "deal_id": deal_id,
        "status": status,
        "current_step": current_step,
        "result_json": result_json,
    }

    return {
        "evaluation_id": evaluation_id,
        "deal_id": deal_id,
        "status": status,
        "current_step": current_step,
        "step_result": step_result,
        "result_json": result_json,
    }


@router.post("/evaluation/pipeline/{deal_id}/evaluation/{evaluation_id}/answers")
async def mock_submit_evaluation_answers(
    deal_id: int, evaluation_id: int, request_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Mock endpoint for submitting evaluation answers
    Simulates POST /api/v1/deals/{deal_id}/evaluation/{evaluation_id}/answers
    """
    answers = request_data.get("answers", {})

    # Get current evaluation state or create new one
    eval_state = MOCK_EVALUATIONS.get(
        evaluation_id,
        {
            "deal_id": deal_id,
            "status": "analyzing",
            "current_step": "vehicle_condition",
            "result_json": {"user_inputs": {}},
        },
    )

    # Update user inputs
    if not eval_state.get("result_json"):
        eval_state["result_json"] = {"user_inputs": {}}
    eval_state["result_json"]["user_inputs"].update(answers)

    current_step = eval_state["current_step"]
    result_json = eval_state["result_json"]

    # Process based on current step
    if current_step == "vehicle_condition":
        # Complete condition assessment
        step_result = {
            "assessment": {
                "condition_score": 8.5,
                "condition_notes": [
                    "Vehicle condition assessment complete",
                    "Overall condition appears good",
                    "No major red flags identified",
                ],
                "recommended_inspection": True,
            },
            "completed": True,
        }
        result_json["vehicle_condition"] = step_result
        next_step = "price"

    elif current_step == "price":
        # Complete price analysis
        step_result = {
            "assessment": {
                "fair_value": 27500,
                "score": 8.8,
                "insights": [
                    "Price is competitive for current market conditions",
                    "Vehicle is priced approximately 3% below fair market value",
                    "Similar vehicles in the area are priced higher",
                ],
                "talking_points": [
                    "Mention comparable vehicles are selling for $28,000-$29,500",
                    "Highlight the good condition to justify the price",
                    "Request maintenance records for additional negotiation leverage",
                ],
            },
            "completed": True,
        }
        result_json["price"] = step_result
        next_step = "financing"

    elif current_step == "financing":
        # Check if financing info provided
        if "financing_type" in answers:
            step_result = {
                "assessment": {
                    "financing_type": answers["financing_type"],
                    "loan_amount": 23500,
                    "estimated_monthly_payment": 438,
                    "estimated_total_cost": 31270,
                    "total_interest": 2770,
                },
                "completed": True,
            }
            result_json["financing"] = step_result
            next_step = "risk"
        else:
            # Ask financing questions
            step_result = {
                "questions": [
                    "What type of financing are you considering? (cash, loan, lease)",
                    "If financing, what is your estimated interest rate? (optional)",
                    "What is your planned down payment amount? (optional)",
                ],
                "required_fields": ["financing_type"],
            }
            eval_state["status"] = "awaiting_input"
            MOCK_EVALUATIONS[evaluation_id] = eval_state

            return {
                "evaluation_id": evaluation_id,
                "deal_id": deal_id,
                "status": "awaiting_input",
                "current_step": current_step,
                "step_result": step_result,
                "result_json": result_json,
            }

    elif current_step == "risk":
        # Complete risk assessment
        step_result = {
            "assessment": {
                "risk_score": 4.5,
                "risk_factors": [
                    "Moderate mileage - monitor maintenance history",
                    "Pre-purchase inspection strongly recommended",
                ],
                "recommendation": "Moderate risk - proceed with caution",
            },
            "completed": True,
        }
        result_json["risk"] = step_result
        next_step = "final"

    elif current_step == "final":
        # Generate final recommendation
        step_result = {
            "assessment": {
                "overall_score": 8.2,
                "recommendation": "Recommended - Good deal with minor considerations",
                "summary": {
                    "condition_score": 8.5,
                    "price_score": 8.8,
                    "risk_score": 4.5,
                },
                "next_steps": [
                    "Schedule a pre-purchase inspection",
                    "Use provided talking points for negotiation",
                    "Review vehicle history report carefully",
                ],
            },
            "completed": True,
        }
        result_json["final"] = step_result
        next_step = None
        eval_state["status"] = "completed"

    else:
        next_step = None

    # Update evaluation state
    if next_step:
        eval_state["current_step"] = next_step
        eval_state["status"] = "analyzing"

    eval_state["result_json"] = result_json
    MOCK_EVALUATIONS[evaluation_id] = eval_state

    return {
        "evaluation_id": evaluation_id,
        "deal_id": deal_id,
        "status": eval_state["status"],
        "current_step": eval_state["current_step"],
        "step_result": step_result,
        "result_json": result_json,
    }


@router.get("/evaluation/pipeline/{deal_id}/evaluation/{evaluation_id}")
async def mock_get_evaluation(deal_id: int, evaluation_id: int) -> dict[str, Any]:
    """
    Mock endpoint for getting evaluation status
    Simulates GET /api/v1/deals/{deal_id}/evaluation/{evaluation_id}
    """
    eval_state = MOCK_EVALUATIONS.get(evaluation_id)

    if not eval_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation {evaluation_id} not found",
        )

    return {
        "id": evaluation_id,
        "user_id": 1,
        "deal_id": deal_id,
        "status": eval_state["status"],
        "current_step": eval_state["current_step"],
        "result_json": eval_state.get("result_json"),
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


# ============================================================================
# Legacy evaluation endpoints (deprecated)
# ============================================================================


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def mock_services_health() -> dict[str, Any]:
    """
    Health check endpoint for mock services
    """
    return {
        "status": "healthy",
        "service": "mock_services",
        "endpoints": {
            "market_check": "available",
            "llm": "available",
            "negotiation": "available",
            "evaluation": "available",
        },
        "message": "All mock services are operational",
    }
