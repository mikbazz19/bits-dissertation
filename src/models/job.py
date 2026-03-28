"""Job description data model"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class JobDescription:
    """Job description data model"""
    title: str
    company: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    required_experience: float = 0.0
    education_requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert job description to dictionary"""
        return {
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'required_experience': self.required_experience,
            'education_requirements': self.education_requirements,
            'responsibilities': self.responsibilities,
            'qualifications': self.qualifications
        }
