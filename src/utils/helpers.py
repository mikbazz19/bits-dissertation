"""Helper utility functions"""

import re
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
    # Pattern for various phone formats
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{10}',
        r'\d{3}-\d{3}-\d{4}'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison"""
    skill = skill.lower().strip()
    # Remove version numbers and special characters
    skill = re.sub(r'[^\w\s+#]', '', skill)
    return skill


def calculate_experience_years(duration_text: str) -> float:
    """Calculate years of experience from duration text"""
    if not duration_text:
        return 0.0
    
    years = 0.0
    months = 0.0
    
    # Extract years
    year_match = re.search(r'(\d+)\s*(?:year|yr)', duration_text, re.IGNORECASE)
    if year_match:
        years = float(year_match.group(1))
    
    # Extract months
    month_match = re.search(r'(\d+)\s*(?:month|mo)', duration_text, re.IGNORECASE)
    if month_match:
        months = float(month_match.group(1))
    
    return years + (months / 12.0)


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
