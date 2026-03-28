"""Entity extraction from resumes"""

import re
from typing import Dict, List, Optional
from ..utils.helpers import extract_email, extract_phone, clean_text


class EntityExtractor:
    """Extract entities like name, email, phone, education from resume"""
    
    def __init__(self):
        self.degree_keywords = [
            'B.Tech', 'B.E.', 'Bachelor', 'M.Tech', 'M.E.', 'Master',
            'MBA', 'PhD', 'Doctorate', 'B.Sc', 'M.Sc', 'BBA', 'MCA',
            'B.Com', 'M.Com', 'BA', 'MA', 'BS', 'MS', 'BSc', 'MSc'
        ]
    
    def extract_all_entities(self, text: str) -> Dict:
        """Extract all entities from resume text"""
        return {
            'name': self.extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'education': self.extract_education(text),
            'certifications': self.extract_certifications(text)
        }
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name (usually at the top of resume)"""
        # Get first few lines
        lines = text.strip().split('\n')[:5]
        
        for line in lines:
            line = line.strip()
            # Name is usually in first lines, capitalized, no special chars
            if line and len(line.split()) <= 4:
                # Check if it looks like a name (mostly letters)
                if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', line):
                    return line
                # Also check for all caps names
                if re.match(r'^[A-Z\s]+$', line) and 2 <= len(line.split()) <= 4:
                    return line.title()
        
        return None
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education_list = []
        
        # Find education section
        education_pattern = r'(?:EDUCATION|Education|ACADEMIC|Academic)(.*?)(?=\n\n[A-Z]{2,}|\Z)'
        match = re.search(education_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            education_text = match.group(1)
        else:
            education_text = text
        
        # Extract degree information
        for degree in self.degree_keywords:
            pattern = rf'{degree}[^a-zA-Z].*?(?:\d{{4}}|\d{{2}})'
            matches = re.finditer(pattern, education_text, re.IGNORECASE)
            
            for match in matches:
                edu_entry = match.group(0)
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', edu_entry)
                year = year_match.group(0) if year_match else None
                
                # Extract institution (often in the same line)
                lines = edu_entry.split('\n')
                institution = None
                for line in lines:
                    if any(word in line.lower() for word in ['university', 'college', 'institute', 'school']):
                        institution = clean_text(line)
                        break
                
                education_list.append({
                    'degree': degree,
                    'institution': institution,
                    'year': year,
                    'raw_text': clean_text(edu_entry)
                })
        
        return education_list
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'(?:AWS|Azure|Google Cloud)\s+Certified\s+[A-Za-z\s]+',
            r'(?:PMP|CISSP|CISA|CEH|CompTIA)\s*[A-Z+]*',
            r'Certified\s+[A-Za-z\s]+(?:Professional|Expert|Associate|Specialist)',
            r'[A-Z]+\s+Certification'
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = clean_text(match.group(0))
                if cert and cert not in certifications:
                    certifications.append(cert)
        
        # Also look in certifications section
        cert_section_pattern = r'(?:CERTIFICATIONS?|Certifications?)(.*?)(?=\n\n[A-Z]{2,}|\Z)'
        match = re.search(cert_section_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            section_text = match.group(1)
            # Extract bullet points or lines
            lines = section_text.split('\n')
            for line in lines:
                line = clean_text(line)
                if line and len(line) > 5 and not line.startswith('•'):
                    line = line.lstrip('• -–')
                    if line and line not in certifications:
                        certifications.append(line)
        
        return certifications[:10]  # Limit to 10
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile URL"""
        pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)[\w-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None
    
    def extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub profile URL"""
        pattern = r'(?:github\.com/)[\w-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text using regex patterns."""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': []
        }
        
        # Extract company names (improved pattern)
        org_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Corporation|Ltd|Limited|LLC|Company|Technologies|Systems|Solutions|Pvt|Private))\.?\b',
            r'\b([A-Z][A-Z]+(?:\s+[A-Z]+)*)\b'  # Acronyms like IBM, NASA
        ]
        
        for pattern in org_patterns:
            orgs = re.findall(pattern, text)
            entities['organizations'].extend(orgs)
        
        entities['organizations'] = list(set(entities['organizations']))[:10]  # Limit to top 10
        
        # Extract years as dates
        year_pattern = r'\b((?:19|20)\d{2})\b'
        entities['dates'] = list(set(re.findall(year_pattern, text)))
        
        # Extract location patterns (City, State)
        location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, ST
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b'  # City, Country
        ]
        
        for pattern in location_patterns:
            locations = re.findall(pattern, text)
            entities['locations'].extend([f"{loc[0]}, {loc[1]}" for loc in locations])
        
        entities['locations'] = list(set(entities['locations']))
        
        return entities
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from text."""
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone (multiple formats)
        phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b',
            r'\b\+\d{1,3}\s?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact['phone'] = phones[0]
                break
        
        # LinkedIn
        linkedin_patterns = [
            r'linkedin\.com/in/([A-Za-z0-9-]+)',
            r'linkedin:\s*([A-Za-z0-9-]+)'
        ]
        for pattern in linkedin_patterns:
            linkedin = re.search(pattern, text, re.IGNORECASE)
            if linkedin:
                contact['linkedin'] = f"linkedin.com/in/{linkedin.group(1)}"
                break
        
        # GitHub
        github_patterns = [
            r'github\.com/([A-Za-z0-9-]+)',
            r'github:\s*([A-Za-z0-9-]+)'
        ]
        for pattern in github_patterns:
            github = re.search(pattern, text, re.IGNORECASE)
            if github:
                contact['github'] = f"github.com/{github.group(1)}"
                break
        
        return contact
