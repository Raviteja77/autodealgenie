"""Test prompt registry and template management"""

import pytest

from app.llm.prompts import PromptTemplate, get_prompt, list_prompts


class TestPromptTemplate:
    """Test PromptTemplate class"""

    def test_prompt_template_creation(self):
        """Test creating a prompt template"""
        template = PromptTemplate(
            id="test_prompt", template="Hello {name}, you are {age} years old."
        )

        assert template.id == "test_prompt"
        assert template.template == "Hello {name}, you are {age} years old."

    def test_prompt_template_format(self):
        """Test formatting a prompt template with variables"""
        template = PromptTemplate(
            id="test_prompt", template="Hello {name}, you are {age} years old."
        )

        formatted = template.format(name="Alice", age=30)
        assert formatted == "Hello Alice, you are 30 years old."

    def test_prompt_template_format_missing_variable(self):
        """Test formatting with missing variable raises KeyError"""
        template = PromptTemplate(
            id="test_prompt", template="Hello {name}, you are {age} years old."
        )

        with pytest.raises(KeyError):
            template.format(name="Alice")  # Missing 'age'


class TestPromptRegistry:
    """Test prompt registry functions"""

    def test_get_prompt_success(self):
        """Test retrieving an existing prompt"""
        prompt = get_prompt("car_recommendation")

        assert prompt.id == "car_recommendation"
        assert isinstance(prompt.template, str)
        assert "{budget}" in prompt.template
        assert "{body_type}" in prompt.template

    def test_get_prompt_not_found(self):
        """Test retrieving a non-existent prompt raises KeyError"""
        with pytest.raises(KeyError) as exc_info:
            get_prompt("nonexistent_prompt")

        assert "nonexistent_prompt" in str(exc_info.value)
        assert "Available prompts:" in str(exc_info.value)

    def test_list_prompts(self):
        """Test listing all available prompts"""
        prompts = list_prompts()

        assert isinstance(prompts, list)
        assert "car_recommendation" in prompts
        assert "negotiation" in prompts
        assert "evaluation" in prompts
        assert "deal_summary" in prompts
        assert "vehicle_comparison" in prompts

    def test_all_registered_prompts_have_templates(self):
        """Test that all registered prompts have valid templates"""
        for prompt_id in list_prompts():
            prompt = get_prompt(prompt_id)
            assert isinstance(prompt.template, str)
            assert len(prompt.template) > 0

    def test_negotiation_prompt_format(self):
        """Test formatting the negotiation prompt"""
        prompt = get_prompt("negotiation")

        formatted = prompt.format(
            make="Honda",
            model="Accord",
            year=2020,
            asking_price=25000,
            mileage=45000,
            condition="good",
            fair_value=23500,
            score=7.5,
        )

        assert "Honda" in formatted
        assert "Accord" in formatted
        assert "2020" in formatted
        assert "$25000" in formatted
        assert "45000" in formatted
        assert "good" in formatted

    def test_evaluation_prompt_format(self):
        """Test formatting the evaluation prompt"""
        prompt = get_prompt("evaluation")

        formatted = prompt.format(
            vin="1HGBH41JXMN109186",
            make="Honda",
            model="Civic",
            year=2019,
            mileage=35000,
            condition="excellent",
            asking_price=22000,
        )

        assert "1HGBH41JXMN109186" in formatted
        assert "Honda" in formatted
        assert "Civic" in formatted
        assert "JSON" in formatted  # Should request JSON format
