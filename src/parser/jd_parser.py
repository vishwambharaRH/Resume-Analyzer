"""
Job Description Parser
Extracts requirements from job descriptions (FR-012)
"""

import re
from typing import Dict, List, Set


class JDParser:
    """Parse job descriptions to extract requirements"""

    # Common skill categories
    PROGRAMMING_LANGUAGES = {
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "ruby",
        "go",
        "rust",
        "php",
        "swift",
        "kotlin",
        "scala",
        "r",
    }

    FRAMEWORKS = {
        "react",
        "angular",
        "vue",
        "django",
        "flask",
        "spring",
        "express",
        "fastapi",
        "nodejs",
        "nextjs",
        "nuxt",
        "laravel",
        "rails",
    }

    DATABASES = {
        "mysql",
        "postgresql",
        "mongodb",
        "redis",
        "cassandra",
        "oracle",
        "sql server",
        "dynamodb",
        "elasticsearch",
        "sqlite",
    }

    CLOUD_TOOLS = {
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
        "ansible",
        "gitlab",
        "github actions",
        "circleci",
    }

    # Education patterns
    EDUCATION_PATTERNS = [
        r"bachelor'?s?\s+(?:degree\s+)?(?:in\s+)?([a-z\s]+)",
        r"master'?s?\s+(?:degree\s+)?(?:in\s+)?([a-z\s]+)",
        r"phd|doctorate",
        r"bs|ms|mba|btech|mtech",
    ]

    # Experience patterns
    EXPERIENCE_PATTERNS = [
        r"(\d+)\+?\s*(?:to\s+\d+)?\s*(?:years?|yrs?)",
        r"(\d+)-(\d+)\s*(?:years?|yrs?)",
        r"minimum\s+(\d+)\s*(?:years?|yrs?)",
        r"at\s+least\s+(\d+)\s*(?:years?|yrs?)",
    ]

    def parse_job_description(self, jd_text: str) -> Dict:
        """
        Parse job description to extract requirements

        Args:
            jd_text: Job description text

        Returns:
            Dictionary with extracted requirements
        """
        # Convert to lowercase for matching
        jd_lower = jd_text.lower()

        # Extract different components
        skills = self._extract_skills(jd_lower)
        education = self._extract_education(jd_lower)
        experience_years = self._extract_experience(jd_lower)
        responsibilities = self._extract_responsibilities(jd_text)

        return {
            "required_skills": skills,
            "required_education": education,
            "required_experience_years": experience_years,
            "responsibilities": responsibilities,
            "total_requirements": len(skills),
        }

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from JD (robust punctuation-safe matcher)"""
        found_skills = set()

        def matches(skill: str) -> bool:
            escaped = re.escape(skill)
            pattern = rf"(?<!\w){escaped}(?!\w)"  # more robust than \b...\b
            return re.search(pattern, text)

        # Programming languages
        for skill in self.PROGRAMMING_LANGUAGES:
            if matches(skill):
                found_skills.add(skill.title())

        # Frameworks
        for skill in self.FRAMEWORKS:
            if matches(skill):
                found_skills.add(skill.title())

        # Databases
        for skill in self.DATABASES:
            if matches(skill):
                found_skills.add(skill.title())

        # Cloud tools
        for skill in self.CLOUD_TOOLS:
            if matches(skill):
                # AWS/GCP/Azure → uppercase, others → title
                found_skills.add(skill.upper() if len(skill) <= 3 else skill.title())

        return sorted(found_skills)

    def _extract_education(self, text: str) -> Dict:
        """Extract education requirements"""
        education = {
            "degree_required": False,
            "degree_level": None,
            "field_of_study": None,
        }

        for pattern in self.EDUCATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education["degree_required"] = True
                if "bachelor" in pattern:
                    education["degree_level"] = "Bachelor's"
                elif "master" in pattern:
                    education["degree_level"] = "Master's"
                elif "phd" in pattern or "doctorate" in pattern:
                    education["degree_level"] = "PhD"

                if match.groups():
                    education["field_of_study"] = match.group(1).strip().title()
                break

        return education

    def _extract_experience(self, text: str) -> int:
        """Extract required years of experience"""
        for pattern in self.EXPERIENCE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                # Get the first number found
                years = int(match.group(1))
                return years

        return 0  # No specific requirement

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from JD"""
        responsibilities = []

        # Look for bullet points or numbered lists
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # Check if line starts with bullet or number
            if re.match(r"^[-•*]\s+", line) or re.match(r"^\d+\.\s+", line):
                # Remove the bullet/number
                resp = re.sub(r"^[-•*\d\.]\s+", "", line).strip()
                if len(resp) > 10:  # Filter out very short items
                    responsibilities.append(resp)

        return responsibilities[:10]  # Return top 10
