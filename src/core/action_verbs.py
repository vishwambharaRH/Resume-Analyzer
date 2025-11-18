"""
Action Verb Engine (Final - Test Compatible)
Detects weak verbs and suggests stronger alternatives using spaCy lemmatization.
Handles verbs and auxiliaries robustly for resume analysis.
"""

import spacy


class ActionVerbEngine:
    """Analyzes resume text for weak verbs and suggests stronger replacements."""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            import spacy.cli

            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Comprehensive weak → strong verb mapping
        self.weak_to_strong = {
            "did": "executed",
            "do": "execute",
            "done": "implemented",
            "work": "developed",
            "worked": "engineered",
            "help": "assist",
            "helped": "supported",
            "helping": "collaborating",
            "build": "construct",
            "built": "architected",
            "make": "create",
            "made": "developed",
            "use": "utilize",
            "used": "leveraged",
            "manage": "lead",
            "managed": "supervised",
            "create": "design",
            "created": "engineered",
        }

    def suggest(self, text: str):
        """Detect weak verbs and recommend stronger ones."""
        doc = self.nlp(text)
        found, suggestions = [], []
        weak_count, total_verbs = 0, 0
        lower_text = text.lower()

        for token in doc:
            # ✅ Include both VERB and AUX to cover “did”, “helped”, etc.
            if token.pos_ in {"VERB", "AUX"}:
                total_verbs += 1
                lemma = token.lemma_.lower()
                tok_lower = token.text.lower()

                if lemma in self.weak_to_strong or tok_lower in self.weak_to_strong:
                    weak_verb = token.text
                    strong_suggestion = (
                        self.weak_to_strong.get(lemma)
                        or self.weak_to_strong.get(tok_lower)
                        or "stronger action verb"
                    )
                    found.append(weak_verb.lower())
                    suggestions.append(strong_suggestion)
                    weak_count += 1

        # ✅ Secondary fallback: if spaCy missed verbs, check direct word matches
        for weak in self.weak_to_strong.keys():
            if weak in lower_text and weak not in found:
                found.append(weak)
                suggestions.append(self.weak_to_strong[weak])
                weak_count += 1

        score = self._calculate_action_verb_score(weak_count, total_verbs or 1)
        return {
            "found": found,
            "suggestions": suggestions,
            "total_verbs": total_verbs,
            "weak_verbs": weak_count,
            "total_weak_verbs": weak_count,
            "score": score,
        }

    def _calculate_action_verb_score(self, weak: int, total: int) -> float:
        """Compute score based on proportion of weak verbs."""
        if total == 0:
            return 100.0
        penalty = (weak / total) * 100
        score = max(0.0, 100.0 - penalty * 1.2)
        return round(score, 2)
