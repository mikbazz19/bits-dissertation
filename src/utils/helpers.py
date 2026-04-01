"""Helper utility functions"""

import re
from datetime import datetime
from typing import List, Optional
import string


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep important punctuation
    text = text.strip()
    return text


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_patterns = [
        r'\+?1?\s*[-.\s]?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}',  # +1 (312) 555-0142 / 312-555-0142
        r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}',                       # (312) 555-0142
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',                        # 312.555.0142 / 312 555 0142
        r'\d{10}',                                              # 3125550142
        r'\+\d{1,3}[-\s]\d{3,4}[-\s]\d{3,4}[-\s]\d{3,4}',   # +40-721-456-789 / +44 7911 123456
        r'\+\d{7,15}',                                         # +40721456789 (compact international)
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison"""
    skill = skill.lower().strip()
    # Remove version numbers and special characters
    skill = re.sub(r'[^\w\s+#]', '', skill)
    return skill


def calculate_experience_years(duration_text: str) -> float:
    """Calculate years of experience from duration text.

    Handles three formats:
    1. Explicit: "2 years 3 months"
    2. Date range: "March 2021 - Present" / "June 2019 - February 2021"
    3. Falls back to 0.0
    """
    if not duration_text:
        return 0.0

    # Format 1: explicit years/months label
    year_match = re.search(r'(\d+)\s*(?:year|yr)', duration_text, re.IGNORECASE)
    month_match = re.search(r'(\d+)\s*(?:month|mo)', duration_text, re.IGNORECASE)
    if year_match or month_match:
        years = float(year_match.group(1)) if year_match else 0.0
        months = float(month_match.group(1)) if month_match else 0.0
        return years + (months / 12.0)

    # Format 2: date range  "Month YYYY – Month YYYY"  or  "Month YYYY – Present"
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    }
    date_pat = r'(?P<sm>[A-Za-z]+)\s+(?P<sy>\d{4})\s*[-–—]\s*(?:(?P<em>[A-Za-z]+)\s+(?P<ey>\d{4})|(?P<present>Present|Current|Now|Till date|Till Date))'
    dm = re.search(date_pat, duration_text, re.IGNORECASE)
    if dm:
        try:
            start_m = month_map.get(dm.group('sm').lower(), 1)
            start_y = int(dm.group('sy'))
            if dm.group('present'):
                end_m = datetime.now().month
                end_y = datetime.now().year
            else:
                end_m = month_map.get(dm.group('em').lower(), 1)
                end_y = int(dm.group('ey'))
            total_months = (end_y - start_y) * 12 + (end_m - start_m)
            return round(max(total_months, 0) / 12.0, 1)
        except Exception:
            pass

    return 0.0


def tokenize_text(text: str) -> List[str]:
    """Simple text tokenization"""
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    return tokens


def similarity_score(list1: List[str], list2: List[str]) -> float:
    """Calculate Jaccard similarity between two lists"""
    if not list1 or not list2:
        return 0.0
    
    set1 = set(normalize_skill(item) for item in list1)
    set2 = set(normalize_skill(item) for item in list2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0
