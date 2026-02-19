"""Resume data model"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Education:
    """Education information"""
    degree: str
    institution: str
    year: Optional[str] = None
    grade: Optional[str] = None


@dataclass
class Experience:
    """Work experience information"""
    title: str
    company: str
    duration: str
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class Resume:
    """Resume data model"""
    raw_text: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    total_experience_years: float = 0.0
    parsed_data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert resume to dictionary"""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'skills': self.skills,
            'education': [
                {
                    'degree': edu.degree,
                    'institution': edu.institution,
                    'year': edu.year,
                    'grade': edu.grade
                } for edu in self.education
            ],
            'experience': [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'duration': exp.duration,
                    'description': exp.description
                } for exp in self.experience
            ],
            'certifications': self.certifications,
            'total_experience_years': self.total_experience_years
        }
