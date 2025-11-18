"""
Unit tests for the Skill Parser (FR-004)
Tests the extract_skills function in isolation.
"""

import pytest
from src.parser.skill_parser import extract_skills

# Note: The 'extract_skills' function sorts its output lists,
# so our expected results must also be in alphabetical order.


def test_extract_skills_technical():
    """Tests if standard technical skills are identified."""
    text = "My skills include Python, React.js, and AWS."
    expected = {"technical_skills": ["AWS", "Python", "React"], "soft_skills": []}
    assert extract_skills(text) == expected


def test_extract_skills_synonyms():
    """Tests that synonyms are correctly mapped."""
    text = "Experienced in Programming in Python and team management."
    expected = {
        "technical_skills": ["Python"],
        "soft_skills": ["Leadership"],  # Assumes "team management" maps to "Leadership"
    }
    assert extract_skills(text) == expected


def test_extract_skills_deduplication():
    """Tests that skills are not listed multiple times."""
    text = "I love Python and I am a Python developer. I also use py."
    expected = {"technical_skills": ["Python"], "soft_skills": []}
    assert extract_skills(text) == expected


def test_extract_skills_no_skills():
    """Tests that no irrelevant words are found."""
    text = "I am a person who likes to go hiking on the weekend."
    expected = {"technical_skills": [], "soft_skills": []}
    assert extract_skills(text) == expected
