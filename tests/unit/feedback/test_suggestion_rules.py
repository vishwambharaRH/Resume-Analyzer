import pytest
from src.feedback.suggestion_rules import get_template_suggestion, TEMPLATE_MAPPINGS

# --- Fixtures/Shared Data ---

# Define the expected output structure for easy assertion
EXPECTED_MINIMALIST = TEMPLATE_MAPPINGS["MINIMALIST"]
EXPECTED_HYBRID = TEMPLATE_MAPPINGS["HYBRID"]
EXPECTED_FUNCTIONAL = TEMPLATE_MAPPINGS["FUNCTIONAL"]

# --- Test Cases ---


def test_suggestion_software_matches_minimalist():
    """
    Verifies that a technical keyword like 'PYTHON' correctly suggests the MINIMALIST template.
    """
    # Input keywords derived from analyzer.py
    keywords = ["Python", "SQL", "Cloud", "Data Analysis"]

    result = get_template_suggestion(keywords)

    # Assert the full object matches the expected minimalist template
    assert result == EXPECTED_MINIMALIST
    assert result["link"] == "../templates/minimalist.txt"


def test_suggestion_sales_matches_hybrid():
    """
    Verifies that a sales/marketing keyword suggests the HYBRID template.
    """
    # Input keywords derived from analyzer.py
    keywords = ["Communication", "Leadership", "SALES", "Negotiation"]

    result = get_template_suggestion(keywords)

    assert result == EXPECTED_HYBRID
    assert result["link"] == "../templates/hybrid.txt"


def test_suggestion_hr_matches_functional():
    """
    Verifies that an HR/entry-level keyword suggests the FUNCTIONAL template.
    """
    # Input keywords derived from analyzer.py
    keywords = ["Recruiting", "HR", "Onboarding", "Training"]

    result = get_template_suggestion(keywords)

    assert result == EXPECTED_FUNCTIONAL
    assert result["link"] == "../templates/functional.txt"


def test_suggestion_prioritizes_first_match():
    """
    Verifies that the logic prioritizes the first matching keyword found in the list.
    Here, 'JAVA' (Minimalist) is prioritized over 'MARKETING' (Hybrid).
    """
    # JAVA is checked before MARKETING
    keywords = ["Time Management", "JAVA", "MARKETING", "Leadership"]

    result = get_template_suggestion(keywords)

    assert result == EXPECTED_MINIMALIST
    assert result["link"] == "../templates/minimalist.txt"


def test_suggestion_default_fallback():
    """
    Verifies that an unmapped or unknown industry keyword correctly returns the DEFAULT (FUNCTIONAL) template.
    """
    # Input keywords that are not in INDUSTRY_RULES
    keywords = ["Gardening", "Cooking", "Photography", "Travel"]

    result = get_template_suggestion(keywords)

    assert result == EXPECTED_FUNCTIONAL
    assert result["description"].startswith("Ideal for students")


def test_suggestion_empty_keywords():
    """
    Verifies handling an empty list of keywords.
    """
    keywords = []

    result = get_template_suggestion(keywords)

    # Empty list should fall back to the default template
    assert result == EXPECTED_FUNCTIONAL
