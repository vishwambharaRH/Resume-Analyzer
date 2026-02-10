# src/feedback/suggestion_rules.py
from typing import List

# Template metadata
TEMPLATE_MAPPINGS = {
    "MINIMALIST": {
        "name": "Minimalist Chronological Template (.txt)",
        "description": "Best for experienced professionals with clear, linear work history (Tech, Finance).",
        "link": "../templates/minimalist.txt",
    },
    "FUNCTIONAL": {
        "name": "Functional/Skills-Based Template (.txt)",
        "description": "Ideal for students or those changing careers, emphasizing skills over dates (Creative, HR).",
        "link": "../templates/functional.txt",
    },
    "HYBRID": {
        "name": "Hybrid/Executive Template (.txt)",
        "description": "Combines chronology and skills summary; good for management and complex careers (Management, Sales).",
        "link": "../templates/hybrid.txt",
    },
}

# Direct keyword → template mapping (this is exactly what tests expect)
INDUSTRY_RULES = {
    # Minimalist (technical)
    "PYTHON": "MINIMALIST",
    "SQL": "MINIMALIST",
    "CLOUD": "MINIMALIST",
    "DATA": "MINIMALIST",
    "JAVA": "MINIMALIST",

    # Hybrid (business/marketing)
    "MARKETING": "HYBRID",
    "SALES": "HYBRID",
    "NEGOTIATION": "HYBRID",

    # Functional (HR / people roles)
    "HR": "FUNCTIONAL",
    "RECRUITING": "FUNCTIONAL",
    "TRAINING": "FUNCTIONAL",

    # Fallback
    "DEFAULT": "FUNCTIONAL",
}


def get_template_suggestion(keywords: List[str]):
    """
    Given a list of keywords, return the full template mapping
    with the correct /static/templates/... path.
    """

    # Normalize keywords
    normalized = [k.upper().strip() for k in keywords]

    # Scan in order for the first matching rule
    for kw in normalized:
        if kw in INDUSTRY_RULES:
            template_key = INDUSTRY_RULES[kw]
            template = TEMPLATE_MAPPINGS[template_key].copy()
            template["link"] = f"../templates/{template_key.lower()}.txt"
            return template

    # Fallback to DEFAULT (FUNCTIONAL)
    fallback_key = INDUSTRY_RULES["DEFAULT"]
    template = TEMPLATE_MAPPINGS[fallback_key].copy()
    template["link"] = f"../templates/{fallback_key.lower()}.txt"
    return template
