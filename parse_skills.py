import spacy as sp
from spacy.matcher import PhraseMatcher
from typing import List

class SkillParser:
    def __init__(self, skills_list: List[str]):
        self.nlp = sp.load("en_core_web_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(skill) for skill in skills_list]
        self.matcher.add("SKILLS", patterns)

    def parse_skills(self, text: str) -> List[str]:
        doc = self.nlp(text)
        matches = self.matcher(doc)
        found_skills = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            found_skills.add(span.text)
        return list(found_skills)