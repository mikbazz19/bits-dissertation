"""
High-level resume parsing helper.
Combines entity, skill, and experience extraction into a single Resume object.
"""

import re
from typing import Dict, List, Optional

from ..models.resume import Resume, Education, Experience
from .entity_extractor import EntityExtractor
from .skill_extractor import SkillExtractor
from .experience_extractor import ExperienceExtractor


# Degree keywords reused for direct OCR-section parsing
_DEGREE_KEYWORDS = [
    'B.Tech', 'B.E.', 'Bachelor', 'M.Tech', 'M.E.', 'Master',
    'MBA', 'PhD', 'Doctorate', 'B.Sc', 'M.Sc', 'BBA', 'MCA',
    'B.Com', 'M.Com', 'BA', 'MA', 'BS', 'MS', 'BSc', 'MSc',
]

# School/pre-degree level markers — require explicit "th" after X/XII to avoid
# matching bare OCR artefacts like "x" or random Roman numerals.
_SCHOOL_LEVEL_RE = re.compile(
    r'\b(?:10th|X\s*th|Matriculation|SSC|SSLC|Secondary\s+School|High\s+School'
    r'|12th|XII\s*th|Intermediate|HSC|\+\s*2|Plus\s+Two|Senior\s+Secondary)\b',
    re.IGNORECASE,
)

# "in Computer Science" / "in Electronics & Communication"
# Use [ \t] (not \s) so the capture never crosses a line boundary
_STREAM_RE = re.compile(
    r'\bin\s+([A-Z][A-Za-z \t&()/]+?)(?=\s+(?:from|at|of)\b|\s*,|\s*[–\-]|\s*\(|\s*\d{4}|\s*$)',
    re.IGNORECASE | re.MULTILINE,
)

# Institution name — stop at comma, newline, parenthesis, a 4-digit year, or GPA/CGPA
# universit\w* covers university/université/universidad/universität/universitatea/etc.
_INST_RE = re.compile(
    r'(?:universit\w+|college|institute|iit|nit|bits|academy|polytechnic|school|facult\w+|hochschule)'
    r'[^,\n(]*?(?=\s*(?:\b(?:19|20)\d{2}\b|\bGPA\b|\bCGPA\b|,|\n|\()|$)',
    re.IGNORECASE,
)

_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def _has_degree_marker(line: str) -> bool:
    """Return True if this line contains a degree or school-level keyword."""
    for kw in _DEGREE_KEYWORDS:
        if re.search(rf'(?<![A-Za-z]){re.escape(kw)}(?![A-Za-z])', line, re.IGNORECASE):
            return True
    return bool(_SCHOOL_LEVEL_RE.search(line))


def _parse_education_group(lines: List[str]) -> Optional[Education]:
    """
    Parse one education entry from a group of consecutive lines.
    Joins with newline so regex anchors stay correct per line.
    """
    # First line should always have the degree; extract it before joining
    # so we don't lose context. Then search the full combined block.
    combined = "\n".join(lines)

    degree = None
    for kw in _DEGREE_KEYWORDS:
        if re.search(rf'(?<![A-Za-z]){re.escape(kw)}(?![A-Za-z])', combined, re.IGNORECASE):
            degree = kw
            break
    if not degree:
        m = _SCHOOL_LEVEL_RE.search(combined)
        if m:
            degree = m.group(0).strip()
    if not degree:
        return None

    # Stream: "in Computer Science"
    sm = _STREAM_RE.search(combined)
    stream = sm.group(1).strip().rstrip(',') if sm else None

    # Institution — search each line; _INST_RE stops before year/GPA
    institution = ""
    for line in lines:
        im = _INST_RE.search(line)
        if im:
            institution = im.group(0).strip().rstrip(' ,')
            break

    # Fallback: if still no institution, the second non-blank, non-degree,
    # non-date line is likely the institution (e.g. foreign-language names)
    if not institution and len(lines) >= 2:
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            # Skip lines that look like dates, GPA, bullets, or are the degree line
            if re.search(r'\b(19|20)\d{2}\b|GPA|CGPA|^[-•*]', line):
                continue
            if _has_degree_marker(line):
                continue
            institution = line.split(',')[0].strip()  # drop trailing country/city
            break

    # Year — take first occurrence
    ym = _YEAR_RE.search(combined)
    year = ym.group(0) if ym else None

    return Education(degree=degree, stream=stream, institution=institution, year=year)


def _education_from_section(section_text: str) -> List[Education]:
    """
    Parse Education objects by grouping multi-line OCR entries.

    A new group starts whenever a line contains a degree or school-level keyword.
    All lines belonging to the same entry (institution, year, GPA, etc.) are
    collected together before parsing so no information is lost.
    """
    # Strip bullet/list markers from the start of each line
    clean_lines = [re.sub(r'^[\s•\-–*►▪]+', '', ln).strip()
                   for ln in section_text.splitlines()]
    clean_lines = [ln for ln in clean_lines if ln]

    # Group: each group starts when a line has a degree marker
    groups: List[List[str]] = []
    current: List[str] = []
    for line in clean_lines:
        if _has_degree_marker(line):
            if current:
                groups.append(current)
            current = [line]
        elif current:
            # Continuation of the current entry (institution line, year, GPA, etc.)
            current.append(line)
        # Lines before any degree keyword are skipped (e.g. section heading leftovers)

    if current:
        groups.append(current)

    education_objs: List[Education] = []
    for group in groups:
        edu = _parse_education_group(group)
        if edu:
            education_objs.append(edu)

    return education_objs


def _certifications_from_section(section_text: str) -> List[str]:
    """Extract certification strings from a pre-split OCR section."""
    certs: List[str] = []
    for line in section_text.splitlines():
        line = re.sub(r'^[\s•\-–*]+', '', line).strip()
        if len(line) > 4:
            certs.append(line)
    return certs[:15]


def _total_years_from_text(text: str, experiences: List[Experience],
                            extractor: ExperienceExtractor) -> float:
    """
    Best-effort total experience calculation.
    1. Look for "X years of experience" phrasing anywhere in the text.
    2. Sum individual durations from parsed Experience objects.
    """
    # Prefer date-range calculation (objective) over self-stated summary claims
    if experiences:
        return extractor.calculate_total_experience(experiences)

    # Fall back to "X years of experience" phrasing only when no entries were parsed
    summary = extractor.extract_experience_summary(text)
    if summary:
        return summary

    return 0.0


def extract_resume_info(text: str, ocr_sections: Optional[Dict] = None) -> Resume:
    """
    Extract structured resume information from plain text.

    Args:
        text: Raw resume text.
        ocr_sections: Optional dict of pre-split sections from OCR
                      (e.g. {'skills': '...', 'experience': '...', ...}).

    Returns:
        A populated Resume dataclass instance.
    """
    sections = ocr_sections or {}

    entity_extractor = EntityExtractor()
    skill_extractor = SkillExtractor()
    experience_extractor = ExperienceExtractor()

    # --- Entities (name, email, phone) ---
    entities = entity_extractor.extract_all_entities(text)

    # --- Skills ---
    skills_text = sections.get("skills") or text
    skills = skill_extractor.extract_skills(skills_text)

    # --- Experience ---
    experience_section = sections.get("experience") or None
    experiences = experience_extractor.extract_experience(text, experience_section=experience_section)

    # --- Total experience years ---
    total_years = _total_years_from_text(text, experiences, experience_extractor)

    # --- Education ---
    education_section = sections.get("education", "")
    if not education_section:
        # Native-text path: slice the education section
        # Allow blank lines after the heading (\n+), stop at next ALL-CAPS section heading
        edu_match = re.search(
            r'(?:^|\n)[^\n]*?(?:EDUCATION|EDUCATI[EO]\b|Academic\s+Background|Qualifications?)[^\n]*\n+'
            r'(.*?)(?=\n[ \t]*[A-Z][A-Z\s]{3,}\n|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )
        if edu_match:
            education_section = edu_match.group(1)

    if education_section:
        education_objs = _education_from_section(education_section)
    else:
        # Last resort: EntityExtractor over full text
        education_objs = [
            Education(
                degree=edu.get("degree", ""),
                stream=edu.get("stream"),
                institution=edu.get("institution") or "",
                year=edu.get("year"),
            )
            for edu in entities.get("education", [])
        ]

    # --- Certifications ---
    cert_section = sections.get("certifications", "")
    if cert_section:
        certifications = _certifications_from_section(cert_section)
    else:
        certifications = entities.get("certifications", [])

    # --- Co-curricular activities ---
    co_curricular = entity_extractor.extract_co_curricular(text)

    return Resume(
        raw_text=text,
        name=entities.get("name"),
        email=entities.get("email"),
        phone=entities.get("phone"),
        linkedin=entities.get("linkedin"),
        github=entities.get("github"),
        skills=skills,
        education=education_objs,
        experience=experiences,
        certifications=certifications,
        co_curricular_activities=co_curricular,
        total_experience_years=total_years,
    )
