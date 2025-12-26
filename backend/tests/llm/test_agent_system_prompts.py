"""Test agent system prompts"""

from app.llm.agent_system_prompts import AGENT_SYSTEM_PROMPTS, get_agent_system_prompt


class TestAgentSystemPrompts:
    """Test agent system prompts dictionary"""

    def test_all_agent_roles_exist(self):
        """Test that all expected agent roles have prompts"""
        expected_roles = ["research", "loan", "negotiation", "evaluator", "qa"]

        for role in expected_roles:
            assert role in AGENT_SYSTEM_PROMPTS
            assert isinstance(AGENT_SYSTEM_PROMPTS[role], str)
            assert len(AGENT_SYSTEM_PROMPTS[role]) > 0

    def test_loan_agent_includes_lender_guidance(self):
        """Test that loan agent prompt includes lender recommendation guidance"""
        loan_prompt = AGENT_SYSTEM_PROMPTS["loan"]

        # Check for lender-related keywords with more specific assertions
        assert "lender" in loan_prompt.lower()
        assert (
            "match score" in loan_prompt.lower()
            or "lender match" in loan_prompt.lower()
            or "matching score" in loan_prompt.lower()
        )
        assert "apr" in loan_prompt.lower()
        assert "features" in loan_prompt.lower() or "benefit" in loan_prompt.lower()

    def test_negotiation_agent_includes_financing_leverage(self):
        """Test that negotiation agent prompt includes financing leverage guidance"""
        negotiation_prompt = AGENT_SYSTEM_PROMPTS["negotiation"]

        # Check for financing leverage keywords with comprehensive validation
        assert "financing" in negotiation_prompt.lower()
        assert "lender" in negotiation_prompt.lower()
        assert "leverage" in negotiation_prompt.lower()
        # Verify pre-approved financing is mentioned
        has_preapproved = (
            "pre-approved" in negotiation_prompt.lower()
            or "preapproved" in negotiation_prompt.lower()
        )
        assert has_preapproved
        # Ensure it's used in context of leverage
        assert "leverage" in negotiation_prompt.lower() and has_preapproved

    def test_evaluator_agent_includes_lender_comparison(self):
        """Test that evaluator agent prompt includes lender comparison guidance"""
        evaluator_prompt = AGENT_SYSTEM_PROMPTS["evaluator"]

        # Check for lender comparison keywords
        assert "lender" in evaluator_prompt.lower()
        assert "financing" in evaluator_prompt.lower()
        assert "total cost" in evaluator_prompt.lower()
        assert "apr" in evaluator_prompt.lower()

    def test_get_agent_system_prompt_with_json_output(self):
        """Test getting agent prompt with JSON output type"""
        prompt = get_agent_system_prompt("loan", "json")

        assert "Senior Auto Financial Specialist" in prompt
        assert "JSON" in prompt
        assert "lender" in prompt.lower()

    def test_get_agent_system_prompt_with_text_output(self):
        """Test getting agent prompt with text output type"""
        prompt = get_agent_system_prompt("negotiation", "text")

        assert "Expert Car Deal Negotiation Advisor" in prompt
        assert "JSON" not in prompt
        assert "financing" in prompt.lower()

    def test_get_agent_system_prompt_unknown_role(self):
        """Test getting prompt for unknown role returns default"""
        prompt = get_agent_system_prompt("unknown_role", "text")

        assert "helpful automotive assistant" in prompt
        assert len(prompt) > 0

    def test_all_agent_prompts_have_personality(self):
        """Test that all agent prompts define personality and expertise"""
        for _role, prompt in AGENT_SYSTEM_PROMPTS.items():
            # Each prompt should define who they are
            assert "You are" in prompt
            # Each prompt should list expertise
            assert "expertise includes" in prompt.lower() or "expertise" in prompt.lower()
            # Each prompt should define their goal
            assert "goal" in prompt.lower()

    def test_loan_agent_prompt_structure(self):
        """Test loan agent prompt has proper structure for lender recommendations"""
        loan_prompt = AGENT_SYSTEM_PROMPTS["loan"]

        # Should mention what to do when lender data is provided
        assert (
            "when lender recommendation data is provided" in loan_prompt.lower()
            or "when lender" in loan_prompt.lower()
        )

        # Should provide guidance on explaining lender recommendations
        assert "explain" in loan_prompt.lower()

    def test_negotiation_agent_prompt_structure(self):
        """Test negotiation agent prompt has proper structure for financing leverage"""
        negotiation_prompt = AGENT_SYSTEM_PROMPTS["negotiation"]

        # Should mention using financing as leverage
        assert "leverage" in negotiation_prompt.lower()
        assert (
            "dealer financing" in negotiation_prompt.lower()
            or "dealer" in negotiation_prompt.lower()
        )

    def test_evaluator_agent_prompt_structure(self):
        """Test evaluator agent prompt has proper structure for total cost analysis"""
        evaluator_prompt = AGENT_SYSTEM_PROMPTS["evaluator"]

        # Should mention comparing total costs
        assert "compare" in evaluator_prompt.lower() or "comparison" in evaluator_prompt.lower()
        assert "total cost" in evaluator_prompt.lower()

        # Should mention considering vehicle price + financing
        assert (
            "vehicle price" in evaluator_prompt.lower()
            or "financing cost" in evaluator_prompt.lower()
        )

    def test_prompts_maintain_original_agent_roles(self):
        """Test that prompts still maintain their original agent personalities"""
        # Loan agent should still be a financial specialist
        assert "Financial Specialist" in AGENT_SYSTEM_PROMPTS["loan"]

        # Negotiation agent should still be a negotiation advisor
        assert "Negotiation Advisor" in AGENT_SYSTEM_PROMPTS["negotiation"]

        # Evaluator should still be a deal evaluator
        assert "Deal Evaluator" in AGENT_SYSTEM_PROMPTS["evaluator"]

    def test_all_prompts_are_comprehensive(self):
        """Test that all prompts are comprehensive (not too short)"""
        for role, prompt in AGENT_SYSTEM_PROMPTS.items():
            # Each prompt should be substantial (at least 200 characters)
            assert len(prompt) >= 200, f"Prompt for {role} is too short"

            # Should have multiple lines
            assert len(prompt.split("\n")) > 3, f"Prompt for {role} lacks structure"
