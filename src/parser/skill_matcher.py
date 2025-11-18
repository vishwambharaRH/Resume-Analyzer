"""
Skill Matching Engine
Matches resume skills with JD requirements (FR-012)
"""

from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher


class SkillMatcher:
    """Match resume skills against job requirements"""

    # Synonym mappings
    SKILL_SYNONYMS = {
        "javascript": ["js", "ecmascript", "javascript"],
        "typescript": ["ts", "typescript"],
        "react": ["reactjs", "react.js", "react"],
        "nodejs": ["node", "node.js", "nodejs"],
        "python": ["python", "python3", "py"],
        "postgresql": ["postgres", "postgresql", "psql"],
        "mongodb": ["mongo", "mongodb"],
        "docker": ["docker", "containerization"],
        "kubernetes": ["k8s", "kube", "kubernetes"],
        "aws": ["amazon web services", "aws"],
        "gcp": ["google cloud", "gcp", "google cloud platform"],
        "azure": ["microsoft azure", "azure"],
        "machine learning": ["ml", "machine learning"],
        "artificial intelligence": ["ai", "artificial intelligence"],
        "c++": ["cpp", "c++", "cplusplus"],
        "c#": ["csharp", "c#"],
    }

    def __init__(self):
        # Create reverse mapping for quick lookup
        self.synonym_map = {}
        for canonical, synonyms in self.SKILL_SYNONYMS.items():
            for syn in synonyms:
                self.synonym_map[syn.lower()] = canonical.lower()

    def match_skills(
        self, resume_skills: List[str], required_skills: List[str]
    ) -> Dict:
        """
        Match resume skills against required skills

        Args:
            resume_skills: Skills from resume
            required_skills: Skills from job description

        Returns:
            Dictionary with matching results
        """
        # Normalize skills
        resume_normalized = {self._normalize_skill(s) for s in resume_skills}
        required_normalized = {self._normalize_skill(s) for s in required_skills}

        matched = set()
        missing = set()
        match_details = []

        for req_skill in required_normalized:
            match_found = False
            match_type = None

            # 1. Exact match
            if req_skill in resume_normalized:
                matched.add(req_skill)
                match_found = True
                match_type = "exact"

            # 2. Synonym match
            elif not match_found:
                for resume_skill in resume_normalized:
                    if self._are_synonyms(req_skill, resume_skill):
                        matched.add(req_skill)
                        match_found = True
                        match_type = "synonym"
                        break

            # 3. Partial match (similarity > 0.8)
            elif not match_found:
                for resume_skill in resume_normalized:
                    similarity = self._calculate_similarity(req_skill, resume_skill)
                    if similarity > 0.8:
                        matched.add(req_skill)
                        match_found = True
                        match_type = "partial"
                        break

            if match_found:
                match_details.append(
                    {
                        "skill": req_skill.title(),
                        "match_type": match_type,
                        "in_resume": True,
                    }
                )
            else:
                missing.add(req_skill)
                match_details.append(
                    {
                        "skill": req_skill.title(),
                        "match_type": "none",
                        "in_resume": False,
                    }
                )

        return {
            "matched_skills": sorted([s.title() for s in matched]),
            "missing_skills": sorted([s.title() for s in missing]),
            "match_details": match_details,
            "match_count": len(matched),
            "total_required": len(required_normalized),
        }

    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        normalized = skill.lower().strip()

        # Check if it's a known synonym
        if normalized in self.synonym_map:
            return self.synonym_map[normalized]

        return normalized

    def _are_synonyms(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are synonyms"""
        norm1 = self._normalize_skill(skill1)
        norm2 = self._normalize_skill(skill2)

        return norm1 == norm2

    def _calculate_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills (0-1)"""
        return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()
