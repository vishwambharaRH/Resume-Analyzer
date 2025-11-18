# dra/mock_data.py

"""
Contains mock data structures for testing purposes.
"""

MOCK_ANALYSIS_REPORT = {
    # PII - Target for anonymization (DRA-97)
    "name": "Alex Johnson",
    "email": "alex.j@example.com",
    "phone": "+91 98765 43210",
    # Core Report Metrics (Target for correctness check - DRA-96)
    "score": 82,
    "match_percentage": 76,
    # Structured Sections
    "sections": {
        "education": [{"degree": "B.Tech", "institution": "PES University"}],
        "skills": ["Python", "Flask", "React", "SQL"],
    },
    # Feedback Data
    "feedback": {
        "missingSections": ["Certifications"],
        "suggestions": [
            "Use stronger action verbs.",
            "Expand on React experience.",
        ],
    },
}
