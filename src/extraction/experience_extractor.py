"""Experience extraction from resumes"""

import re
from typing import List, Dict, Optional
from datetime import datetime
from ..models.resume import Experience
from ..utils.helpers import calculate_experience_years


class ExperienceExtractor:
    """Extract work experience information from resume text"""
    
    def __init__(self):
        self.month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]
    
    def extract_experience(self, text: str, experience_section: str = None) -> List[Experience]:
        """Extract work experience entries from text"""
        # Use experience section if provided, otherwise use full text
        search_text = experience_section if experience_section else text
        
        if not search_text:
            return []
        
        experiences = []
        
        # Pattern to match experience entries
        # Looking for patterns like: Job Title at Company (Date - Date)
        patterns = [
            # Pattern 1: Title at Company, Date - Date
            r'([A-Z][A-Za-z\s&]+(?:Engineer|Developer|Manager|Analyst|Scientist|Consultant|Designer|Architect|Lead|Director|Specialist))\s+(?:at|@)\s+([A-Z][A-Za-z\s&\.]+)[\s\n]+([A-Za-z]+\s+\d{4}\s*[-–—]\s*(?:[A-Za-z]+\s+\d{4}|Present|Current))',
            
            # Pattern 2: Company - Title (Date - Date)
            r'([A-Z][A-Za-z\s&\.]+)[\s\n]+([A-Z][A-Za-z\s&]+(?:Engineer|Developer|Manager|Analyst|Scientist|Consultant|Designer|Architect|Lead|Director|Specialist))[\s\n]+([A-Za-z]+\s+\d{4}\s*[-–—]\s*(?:[A-Za-z]+\s+\d{4}|Present|Current))'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, search_text, re.MULTILINE)
            
            for match in matches:
                if len(match.groups()) >= 3:
                    # Extract components
                    title = match.group(1).strip()
                    company = match.group(2).strip()
                    duration = match.group(3).strip()
                    
                    # Extract description (text following the match)
                    start_pos = match.end()
                    description = self._extract_description(search_text, start_pos)
                    
                    # Parse dates
                    start_date, end_date = self._parse_dates(duration)
                    
                    experience = Experience(
                        title=title,
                        company=company,
                        duration=duration,
                        description=description,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    experiences.append(experience)
        
        return experiences
    
    def calculate_total_experience(self, experiences: List[Experience]) -> float:
        """Calculate total years of experience"""
        total_years = 0.0
        
        for exp in experiences:
            years = calculate_experience_years(exp.duration)
            total_years += years
        
        return round(total_years, 1)
    
    def extract_experience_summary(self, text: str) -> Optional[float]:
        """Extract total years of experience mentioned in summary"""
        patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'experience\s+of\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+in\s+(?:the\s+)?(?:field|industry)',
            r'over\s+(\d+)\+?\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_description(self, text: str, start_pos: int, max_length: int = 500) -> str:
        """Extract job description following an experience entry"""
        # Get text after the match
        remaining_text = text[start_pos:start_pos + max_length]
        
        # Stop at next job entry or section header
        stop_patterns = [
            r'\n[A-Z][A-Za-z\s&]+(?:at|@)',  # Next job
            r'\n\n[A-Z]{2,}',  # Section header
            r'\n(?:EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS)'  # Common sections
        ]
        
        for pattern in stop_patterns:
            match = re.search(pattern, remaining_text)
            if match:
                remaining_text = remaining_text[:match.start()]
                break
        
        # Clean and return
        description = remaining_text.strip()
        # Take first few lines if too long
        lines = description.split('\n')[:5]
        return '\n'.join(lines).strip()
    
    def _parse_dates(self, duration_str: str) -> tuple:
        """Parse start and end dates from duration string"""
        # Split by dash/hyphen
        parts = re.split(r'\s*[-–—]\s*', duration_str)
        
        start_date = parts[0].strip() if len(parts) > 0 else None
        end_date = parts[1].strip() if len(parts) > 1 else None
        
        # Standardize "Present" or "Current"
        if end_date and re.match(r'(?:present|current)', end_date, re.IGNORECASE):
            end_date = "Present"
        
        return start_date, end_date
    
    def extract_current_position(self, experiences: List[Experience]) -> Optional[Experience]:
        """Get current/most recent position"""
        current_keywords = ['present', 'current', 'ongoing']
        
        for exp in experiences:
            if exp.end_date and any(keyword in exp.end_date.lower() for keyword in current_keywords):
                return exp
        
        # Return first one if no current position found
        return experiences[0] if experiences else None
