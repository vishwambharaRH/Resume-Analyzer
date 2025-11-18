"""
Unit tests for JD Matcher (FR-012)
Implements DRA-72
"""

import pytest
from src.parser.jd_matcher import JDMatcher
from src.parser.jd_parser import JDParser
from src.parser.skill_matcher import SkillMatcher


class TestJDParser:
    """Test job description parsing"""

    def setup_method(self):
        self.parser = JDParser()

    def test_extract_skills_from_jd(self):
        """Test skill extraction from job description"""
        jd_text = """
        We are looking for a Senior Software Engineer with expertise in
        Python, JavaScript, React, and AWS. Experience with Docker and
        Kubernetes is a plus.
        """

        result = self.parser.parse_job_description(jd_text)

        assert "Python" in result["required_skills"]
        assert "React" in result["required_skills"]
        assert "AWS" in result["required_skills"]

    def test_extract_experience_requirements(self):
        """Test experience extraction"""
        jd_text = "Looking for candidates with 5+ years of experience"

        result = self.parser.parse_job_description(jd_text)

        assert result["required_experience_years"] == 5

    def test_extract_education_requirements(self):
        """Test education extraction"""
        jd_text = "Bachelor's degree in Computer Science required"

        result = self.parser.parse_job_description(jd_text)

        assert result["required_education"]["degree_required"] == True
        assert "Bachelor" in result["required_education"]["degree_level"]

    def test_no_experience_requirement(self):
        """Test JD without experience requirement"""
        jd_text = "Python developer needed"
        result = self.parser.parse_job_description(jd_text)
        assert result["required_experience_years"] == 0

    def test_no_education_requirement(self):
        """Test JD without education requirement"""
        jd_text = "Python developer needed"
        result = self.parser.parse_job_description(jd_text)
        assert result["required_education"]["degree_required"] == False


class TestSkillMatcher:
    """Test skill matching algorithm"""

    def setup_method(self):
        self.matcher = SkillMatcher()

    def test_exact_match(self):
        """Test exact skill matching"""
        resume_skills = ["Python", "JavaScript", "React"]
        required_skills = ["Python", "JavaScript"]

        result = self.matcher.match_skills(resume_skills, required_skills)

        assert result["match_count"] == 2
        assert "Python" in result["matched_skills"]

    def test_synonym_match(self):
        """Test synonym matching (React.js = React)"""
        resume_skills = ["React.js", "Node"]
        required_skills = ["React", "NodeJS"]

        result = self.matcher.match_skills(resume_skills, required_skills)

        assert result["match_count"] >= 1

    def test_missing_skills_detection(self):
        """Test detection of missing skills"""
        resume_skills = ["Python", "JavaScript"]
        required_skills = ["Python", "JavaScript", "AWS", "Docker"]

        result = self.matcher.match_skills(resume_skills, required_skills)

        assert len(result["missing_skills"]) == 2

    def test_empty_resume_skills(self):
        """Test with no resume skills"""
        result = self.matcher.match_skills([], ["Python", "AWS"])
        assert result["match_count"] == 0
        assert len(result["missing_skills"]) == 2

    def test_empty_required_skills(self):
        """Test with no required skills"""
        result = self.matcher.match_skills(["Python"], [])
        assert result["total_required"] == 0


class TestJDMatcher:
    """Test complete matching flow"""

    def setup_method(self):
        self.matcher = JDMatcher()

    def test_high_fit_percentage(self):
        """Test calculation with high fit"""
        resume_data = {
            "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
            "experience": "5 years as Software Engineer",
            "education": "Bachelor's in Computer Science",
        }

        jd_text = """
        Looking for Software Engineer with Python, JavaScript, React, AWS.
        3+ years experience required. Bachelor's degree in CS.
        """

        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        assert result["fit_percentage"] >= 70
        assert result["fit_category"] in ["Good Fit", "Excellent Fit"]

    def test_low_fit_percentage(self):
        """Test calculation with low fit"""
        resume_data = {
            "skills": ["Java", "Spring"],
            "experience": "2 years",
            "education": "",
        }

        jd_text = """
        Senior Python Developer with 8+ years experience.
        Master's degree required. Skills: Python, Django, AWS, Docker.
        """

        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        assert result["fit_percentage"] < 50

    def test_recommendations_generated(self):
        """Test that recommendations are generated"""
        resume_data = {
            "skills": ["Python"],
            "experience": "3 years",
            "education": "BS CS",
        }

        jd_text = "Looking for Python, AWS, Docker expertise"

        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        assert len(result["recommendations"]) > 0

    def test_weighted_calculation(self):
        """Test that weights are applied correctly (60/20/20)"""
        resume_data = {
            "skills": ["Python", "JavaScript", "React"],
            "experience": "No experience",
            "education": "",
        }

        jd_text = "Python, JavaScript, React required"

        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        # Should be around 60% (skills only, 100% * 0.6)
        assert 55 <= result["fit_percentage"] <= 65

    def test_all_skills_matched(self):
        """Test when all skills are matched"""
        resume_data = {
            "skills": ["Python", "AWS", "Docker"],
            "experience": "5 years",
            "education": "BS CS",
        }

        jd_text = "Python, AWS, Docker required. 5+ years. Bachelor's degree."

        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        assert len(result["missing_skills"]) == 0
        assert "✅" in result["recommendations"][0]

    def test_fit_categories(self):
        """Test all fit category boundaries"""
        matcher = JDMatcher()

        assert matcher._get_fit_category(85) == "Excellent Fit"
        assert matcher._get_fit_category(70) == "Good Fit"
        assert matcher._get_fit_category(50) == "Moderate Fit"
        assert matcher._get_fit_category(30) == "Poor Fit"

    def test_experience_match_no_requirement(self):
        """Test experience when JD has no requirement"""
        resume_data = {"experience": "5 years", "skills": [], "education": ""}
        result = self.matcher._calculate_experience_match(resume_data, 0)
        assert result == 0.0

    def test_experience_match_exact(self):
        """Test exact experience match"""
        resume_data = {"experience": "5 years engineer", "skills": [], "education": ""}
        result = self.matcher._calculate_experience_match(resume_data, 5)
        assert result == 100.0

    def test_experience_match_insufficient(self):
        """Test insufficient experience"""
        resume_data = {"experience": "2 years", "skills": [], "education": ""}
        result = self.matcher._calculate_experience_match(resume_data, 5)
        assert result == 40.0

    def test_education_match_no_requirement(self):
        """Test education when JD has no requirement"""
        resume_data = {"education": "BS CS", "skills": [], "experience": ""}
        result = self.matcher._calculate_education_match(resume_data, {})
        assert result == 0.0

    def test_education_match_bachelor(self):
        """Test bachelor's degree match"""
        resume_data = {
            "education": "Bachelor in Computer Science",
            "skills": [],
            "experience": "",
        }
        req = {"degree_required": True, "degree_level": "Bachelor's"}
        result = self.matcher._calculate_education_match(resume_data, req)
        assert result == 100.0

    def test_education_match_no_degree(self):
        """Test when resume has no degree"""
        resume_data = {"education": "", "skills": [], "experience": ""}
        req = {"degree_required": True, "degree_level": "Bachelor's"}
        result = self.matcher._calculate_education_match(resume_data, req)
        assert result == 0.0

    def test_string_skills_conversion(self):
        """Test when skills are provided as string"""
        resume_data = {
            "skills": "Python JavaScript React",
            "experience": "",
            "education": "",
        }

        jd_text = "Python JavaScript required"
        result = self.matcher.match_resume_to_jd(resume_data, jd_text)

        assert result["fit_percentage"] > 0
