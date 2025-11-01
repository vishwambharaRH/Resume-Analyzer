# TODO: Implement the following
# As a recruiter
# I want the system to extract key skills from resumes
# So that I can quickly see the candidate’s competencies.

# Acceptance Criteria:

# Keywords must be extracted and placed in a list.

# Synonyms must be given marks based on relative complexity of word, the more complex the better.

# Parsing logic must be memory-sound.

import spacy as sp
from spacy.matcher import PhraseMatcher
from typing import List

class SkillParser:
    def __init__(self, skill_keywords: List[str], synonym_map: dict):
        self.nlp = sp.load("en_core_web_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(text) for text in skill_keywords]
        self.matcher.add("SKILL", patterns)
        self.synonym_map = synonym_map

    def parse_skills(self, text: str) -> List[dict]:
        doc = self.nlp(text)
        matches = self.matcher(doc)
        extracted_skills = []

        for match_id, start, end in matches:
            skill = doc[start:end].text
            complexity_score = self.get_complexity_score(skill)
            extracted_skills.append({
                "skill": skill,
                "complexity_score": complexity_score
            })

        return extracted_skills

    def get_complexity_score(self, skill: str) -> int:
        for synonym, score in self.synonym_map.items():
            if skill.lower() == synonym.lower():
                return score
        return 1  # Default score for unlisted skills
    
    
    
