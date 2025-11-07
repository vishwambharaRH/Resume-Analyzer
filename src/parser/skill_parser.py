"""
Skill Parsing Module - FR-004 Implementation
Implements FR-004: Extract key skills (keywords, synonyms).
"""

import json
import pdfplumber
import docx
import spacy
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
from spacy.matcher import PhraseMatcher

# --- 1. Setup spaCy Matcher ---

# Load model (make sure you've run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = spacy.blank("en")  # Fallback


# Load skill dictionaries from the root folder
def load_skill_dictionaries(
    folder_path: str = "skill_lists",
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Loads all skill JSON files from a directory."""
    skill_dir = Path(folder_path)
    if not skill_dir.exists():
        print(
            f"Warning: '{folder_path}' directory not found. Skill extractor will find 0 skills."
        )
        return {}, {}

    tech_file = skill_dir / "technical_skills.json"
    soft_file = skill_dir / "soft_skills.json"

    technical_skills = (
        json.loads(tech_file.read_text(encoding="utf-8")) if tech_file.exists() else {}
    )
    soft_skills = (
        json.loads(soft_file.read_text(encoding="utf-8")) if soft_file.exists() else {}
    )

    return technical_skills, soft_skills


# Build the PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
skill_categories: Dict[str, str] = {}

technical_skills, soft_skills = load_skill_dictionaries()
if not technical_skills and not soft_skills:
    print("Warning: No skill dictionaries loaded. Skill extractor will find 0 skills.")
else:
    for canonical_name, variants in technical_skills.items():
        skill_categories[canonical_name] = "technical"
        patterns = [nlp.make_doc(variant) for variant in variants]
        matcher.add(canonical_name, patterns)
    for canonical_name, variants in soft_skills.items():
        skill_categories[canonical_name] = "soft"
        patterns = [nlp.make_doc(variant) for variant in variants]
        matcher.add(canonical_name, patterns)


# --- 2. Core Skill Extraction Function (Your FR-004) ---


def extract_skills(resume_text: str) -> Dict[str, List[str]]:
    """
    Extracts technical and soft skills from a given text.
    """
    doc = nlp(resume_text, disable=["ner", "parser"])
    matches = matcher(doc)

    found_technical: Set[str] = set()
    found_soft: Set[str] = set()

    for match_id, start, end in matches:
        canonical_name = nlp.vocab.strings[match_id]
        category = skill_categories.get(canonical_name)

        if category == "technical":
            found_technical.add(canonical_name)
        elif category == "soft":
            found_soft.add(canonical_name)

    return {
        "technical_skills": sorted(list(found_technical)),
        "soft_skills": sorted(list(found_soft)),
    }


# --- 3. Parsing Function (Used by the worker) ---


def get_text_from_parser(file_path: Path) -> str:
    """
    Reads a file and returns its raw text content.
    Supports .pdf, .docx, and .txt.
    """
    text = ""
    suffix = file_path.suffix

    try:
        if suffix == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif suffix == ".docx":
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif suffix == ".txt":
            text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        # Re-raise to be caught by the job handler
        raise

    return text
