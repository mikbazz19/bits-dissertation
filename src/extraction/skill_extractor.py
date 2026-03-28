"""Skill extraction from resumes and job descriptions"""

import re
import json
from pathlib import Path
from typing import List, Set, Dict
from ..utils.config import Config
from ..utils.helpers import normalize_skill


class SkillExtractor:
    """Extract skills from text using pattern matching and predefined skill database"""
    
    def __init__(self, skills_db_path: Path = None):
        """Initialize with skills database"""
        if skills_db_path is None:
            skills_db_path = Config.SKILLS_DATABASE
        
        self.skills_database = self._load_skills_database(skills_db_path)
        self.skill_categories = self._build_skill_categories()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Match against skills database
        for skill in self.skills_database:
            skill_lower = skill.lower()
            # Direct match or word boundary match
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into technical, soft, and domain-specific"""
        categorized = {
            'technical': [],
            'soft': [],
            'domain': [],
            'tools': [],
            'languages': []
        }
        
        for skill in skills:
            skill_norm = normalize_skill(skill)
            
            # Check each category
            for category, category_skills in self.skill_categories.items():
                if skill_norm in [normalize_skill(s) for s in category_skills]:
                    if category in categorized:
                        categorized[category].append(skill)
                    break
            else:
                # Default to technical if not categorized
                categorized['technical'].append(skill)
        
        return categorized
    
    def extract_from_section(self, text: str, section_text: str) -> List[str]:
        """Extract skills from a specific section of the resume"""
        if not section_text:
            return self.extract_skills(text)
        
        return self.extract_skills(section_text)
    
    def _load_skills_database(self, skills_db_path: Path) -> List[str]:
        """Load skills database from JSON file"""
        if not skills_db_path.exists():
            # Return default skills if database doesn't exist
            return self._get_default_skills()
        
        try:
            with open(skills_db_path, 'r') as f:
                data = json.load(f)
                return data.get('skills', self._get_default_skills())
        except Exception:
            return self._get_default_skills()
    
    def _get_default_skills(self) -> List[str]:
        """Return default list of common skills"""
        return [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB',
            
            # Web Technologies
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django',
            'Flask', 'Spring Boot', 'Express.js', 'Next.js', 'REST API', 'GraphQL',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
            'Cassandra', 'DynamoDB', 'Firebase', 'SQLite',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
            'CI/CD', 'Terraform', 'Ansible', 'Git', 'GitHub', 'GitLab',
            
            # Data Science & ML
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Pandas', 'NumPy', 'NLP', 'Computer Vision', 'Data Analysis', 'Statistics',
            'Keras', 'OpenCV', 'NLTK', 'spaCy',
            
            # Tools & Frameworks
            'Linux', 'Unix', 'Windows', 'Agile', 'Scrum', 'JIRA', 'Confluence',
            'Visual Studio', 'VS Code', 'IntelliJ', 'Eclipse',
            
            # Soft Skills
            'Communication', 'Leadership', 'Teamwork', 'Problem Solving',
            'Critical Thinking', 'Time Management', 'Adaptability', 'Creativity',
            
            # Other Technical Skills
            'Microservices', 'System Design', 'Object-Oriented Programming',
            'Data Structures', 'Algorithms', 'API Development', 'Testing',
            'Unit Testing', 'Integration Testing', 'Security', 'Networking'
        ]
    
    def _build_skill_categories(self) -> Dict[str, List[str]]:
        """Build categorized skills dictionary"""
        return {
            'languages': [
                'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
                'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB'
            ],
            'technical': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django',
                'Flask', 'Spring Boot', 'Express.js', 'REST API', 'GraphQL',
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
                'AWS', 'Azure', 'Google Cloud', 'Microservices', 'System Design'
            ],
            'tools': [
                'Git', 'GitHub', 'GitLab', 'Jenkins', 'JIRA', 'Confluence',
                'Visual Studio', 'VS Code', 'IntelliJ', 'Docker', 'Kubernetes'
            ],
            'domain': [
                'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
                'Data Analysis', 'Statistics', 'TensorFlow', 'PyTorch'
            ],
            'soft': [
                'Communication', 'Leadership', 'Teamwork', 'Problem Solving',
                'Critical Thinking', 'Time Management', 'Adaptability', 'Creativity'
            ]
        }
