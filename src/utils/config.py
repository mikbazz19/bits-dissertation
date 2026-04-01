"""Configuration settings for the application"""

import os
from pathlib import Path


class Config:
    """Application configuration"""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    SAMPLE_RESUMES_DIR = DATA_DIR / "sample_resumes"
    SAMPLE_JOBS_DIR = DATA_DIR / "sample_jobs"
    
    # Skills database
    SKILLS_DATABASE = DATA_DIR / "skills_database.json"
    
    # NLP Model settings
    SPACY_MODEL = "en_core_web_sm"
    
    # Matching thresholds
    SKILL_MATCH_THRESHOLD = 0.6
    OVERALL_MATCH_THRESHOLD = 0.5

    # Scoring weights  (must sum to 1.0)
    SKILLS_WEIGHT = 0.6
    EXPERIENCE_WEIGHT = 0.3
    EDUCATION_WEIGHT = 0.1

    # Decision thresholds (percentage points, post-confidence)
    ACCEPT_THRESHOLD = 75   # >= Accept
    REVIEW_THRESHOLD = 60   # >= Review, else Reject

    # Overqualification: reject if candidate exp exceeds required by more than this
    OVERQUALIFICATION_YEARS_BUFFER = 3
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SAMPLE_RESUMES_DIR.mkdir(exist_ok=True)
        cls.SAMPLE_JOBS_DIR.mkdir(exist_ok=True)
