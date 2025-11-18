"""
Job Description Matcher
Complete matching engine combining all components (FR-012)
"""

from typing import Dict, List
from .jd_parser import JDParser
from .skill_matcher import SkillMatcher


class JDMatcher:
    """Main matcher for resume vs job description"""

    # Weights for fit calculation
    SKILL_WEIGHT = 0.60
    EXPERIENCE_WEIGHT = 0.20
    EDUCATION_WEIGHT = 0.20

    def __init__(self):
        self.jd_parser = JDParser()
        self.skill_matcher = SkillMatcher()

    def match_resume_to_jd(self, resume_data: Dict, jd_text: str) -> Dict:
        """
        Match resume against job description

        Args:
            resume_data: Parsed resume data with skills, education, experience
            jd_text: Job description text

        Returns:
            Complete matching results with fit percentage
        """
        # Parse job description
        jd_requirements = self.jd_parser.parse_job_description(jd_text)

        # Extract resume data
        resume_skills = resume_data.get("skills", [])
        if isinstance(resume_skills, str):
            resume_skills = [s.strip() for s in resume_skills.split() if s.strip()]

        # Match skills
        skill_match = self.skill_matcher.match_skills(
            resume_skills, jd_requirements.get("required_skills", [])
        )

        # Calculate skill match percentage (0-100)
        skill_percentage = self._calculate_skill_match(skill_match)

        # Calculate experience match (0-100). IMPORTANT: if JD didn't specify years, returns 0.0
        experience_percentage = self._calculate_experience_match(
            resume_data, jd_requirements.get("required_experience_years", 0)
        )

        # Calculate education match (0-100). IMPORTANT: if JD doesn't require degree, returns 0.0
        education_percentage = self._calculate_education_match(
            resume_data, jd_requirements.get("required_education", {})
        )

        # Calculate overall fit using weights
        overall_fit = (
            skill_percentage * self.SKILL_WEIGHT
            + experience_percentage * self.EXPERIENCE_WEIGHT
            + education_percentage * self.EDUCATION_WEIGHT
        )

        # Determine fit category
        fit_category = self._get_fit_category(overall_fit)

        # Generate recommendations
        recommendations = self._generate_recommendations(skill_match, jd_requirements)

        return {
            "fit_percentage": round(overall_fit, 1),
            "fit_category": fit_category,
            "matched_skills": skill_match.get("matched_skills", []),
            "missing_skills": skill_match.get("missing_skills", []),
            "skill_match_percentage": round(skill_percentage, 1),
            "experience_match_percentage": round(experience_percentage, 1),
            "education_match_percentage": round(education_percentage, 1),
            "recommendations": recommendations,
            "explanation": self._generate_explanation(
                overall_fit,
                skill_percentage,
                experience_percentage,
                education_percentage,
            ),
            "match_details": skill_match.get("match_details", {}),
        }

    def _calculate_skill_match(self, skill_match: Dict) -> float:
        """Calculate skill match percentage (0-100)."""
        total_required = skill_match.get("total_required", 0)
        match_count = skill_match.get(
            "match_count", skill_match.get("matched_count", 0)
        )

        # If there are zero required skills, contribution is 0 (tests expect skills-only JD weighted)
        if total_required == 0:
            return 0.0

        return (match_count / total_required) * 100

    def _calculate_experience_match(
        self, resume_data: Dict, required_years: int
    ) -> float:
        """
        Calculate experience match percentage (0-100).

        If JD does not specify required_years (==0) we treat contribution as 0 (tests expect this).
        """
        if required_years == 0:
            return 0.0

        experience_text = resume_data.get("experience", "")

        # Handle empty / explicit "no experience"
        if (
            not isinstance(experience_text, str)
            or not experience_text.strip()
            or experience_text.strip().lower() in {"no experience", "none", "n/a"}
        ):
            estimated_years = 0
        else:
            import re

            num_match = re.search(
                r"(\d+)\s*\+?\s*(?:years?|yrs?)", experience_text.lower()
            )
            if num_match:
                try:
                    estimated_years = int(num_match.group(1))
                except Exception:
                    estimated_years = 0
            else:
                job_count = (
                    experience_text.lower().count("engineer")
                    + experience_text.lower().count("developer")
                    + experience_text.lower().count("analyst")
                    + experience_text.lower().count("manager")
                )
                estimated_years = job_count * 2

        if estimated_years >= required_years and required_years > 0:
            return 100.0
        elif required_years > 0:
            return (estimated_years / required_years) * 100
        else:
            return 0.0

    def _calculate_education_match(
        self, resume_data: Dict, required_education: Dict
    ) -> float:
        """
        Calculate education match percentage (0-100).

        If JD does not require a degree, treat contribution as 0%.
        """
        if not required_education or not required_education.get(
            "degree_required", False
        ):
            return 0.0

        education_text = resume_data.get("education", "")
        if not isinstance(education_text, str) or not education_text.strip():
            return 0.0

        level = required_education.get("degree_level")
        if level:
            level_l = level.lower()
            ed_l = education_text.lower()
            if "bachelor" in level_l and any(
                term in ed_l for term in ["bachelor", "bs", "b.tech", "btech"]
            ):
                return 100.0
            elif "master" in level_l and any(
                term in ed_l for term in ["master", "ms", "m.tech", "mtech"]
            ):
                return 100.0
            elif "phd" in level_l and any(
                term in ed_l for term in ["phd", "doctorate"]
            ):
                return 100.0

        if any(
            term in education_text.lower()
            for term in ["degree", "bachelor", "master", "bs", "ms", "b.tech", "m.tech"]
        ):
            return 75.0

        return 50.0

    def _get_fit_category(self, fit_percentage: float) -> str:
        if fit_percentage >= 80:
            return "Excellent Fit"
        elif fit_percentage >= 60:
            return "Good Fit"
        elif fit_percentage >= 40:
            return "Moderate Fit"
        else:
            return "Poor Fit"

    def _generate_recommendations(
        self, self_skill_match: Dict, jd_requirements: Dict
    ) -> List[str]:
        recommendations = []
        if self_skill_match is None:
            return recommendations

        missing = self_skill_match.get("missing_skills", []) or self_skill_match.get(
            "missing", []
        )
        if not missing:
            recommendations.append(
                "✅ Your resume matches all required skills! Great job!"
            )
            return recommendations

        if len(missing) <= 3:
            for skill in missing:
                recommendations.append(
                    f"🎯 Add {skill} experience to strengthen your profile. Consider taking online courses or building a project."
                )
        else:
            recommendations.append(
                f"🎯 Focus on acquiring these critical skills: {', '.join(missing[:3])}"
            )
            recommendations.append(
                f"📚 Additional skills to consider: {', '.join(missing[3:6])}"
            )

        return recommendations

    def _generate_explanation(
        self, overall_fit: float, skill_pct: float, exp_pct: float, edu_pct: float
    ) -> str:
        explanation = (
            f"Your resume shows a {overall_fit:.1f}% match with this position. "
        )
        if skill_pct < 60:
            explanation += f"Your skill match is {skill_pct:.1f}%, which could be improved by acquiring the missing technical skills. "
        else:
            explanation += f"You have a strong skill match at {skill_pct:.1f}%. "
        if exp_pct < 80 and exp_pct > 0:
            explanation += f"Your experience level ({exp_pct:.1f}% match) may need additional development. "
        if edu_pct > 0 and edu_pct < 100:
            explanation += (
                f"Consider highlighting relevant education or certifications."
            )
        return explanation.strip()
