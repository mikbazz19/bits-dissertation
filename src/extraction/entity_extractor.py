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
    
    # LinkedIn profile URL
    _LINKEDIN_RE = re.compile(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?',
        re.IGNORECASE
    )

    # GitHub profile URL (matches github.com/user or github.com/user/repo —
    # we keep the full matched URL so the link works as-is)
    _GITHUB_RE = re.compile(
        r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+(?:/[\w\-\.]+)?',
        re.IGNORECASE
    )

    def extract_all_entities(self, text: str) -> Dict:
        """Extract all entities from resume text"""
        return {
            'name': self.extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'education': self.extract_education(text),
            'certifications': self.extract_certifications(text),
            'linkedin': self.extract_linkedin(text),
            'github': self.extract_github(text),
        }
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Return the first LinkedIn profile URL found, normalised to https://."""
        m = self._LINKEDIN_RE.search(text)
        if not m:
            return None
        url = m.group(0)
        if not url.lower().startswith('http'):
            url = 'https://' + url
        return url

    def extract_github(self, text: str) -> Optional[str]:
        """Return the first GitHub URL found, normalised to https://."""
        m = self._GITHUB_RE.search(text)
        if not m:
            return None
        url = m.group(0)
        if not url.lower().startswith('http'):
            url = 'https://' + url
        return url

    # Common honorific prefixes that precede names
    _HONORIFIC_RE = re.compile(
        r'^(?:Dr|Mr|Mrs|Ms|Miss|Prof|Rev|Sir|Mx)\.?\s+',
        re.IGNORECASE
    )

    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name (usually at the top of resume)"""
        lines = text.strip().split('\n')[:6]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Strip honorific prefix (Dr., Mr., Prof., etc.) before matching
            name_part = self._HONORIFIC_RE.sub('', line).strip()

            words = name_part.split()
            if len(words) < 2 or len(words) > 5:
                continue

            # Title-case with unicode support and optional hyphens.
            # Require at least one lowercase letter so all-caps falls through.
            if (re.match(
                    r'^[A-Za-zÀ-ÖØ-öø-ÿ\u0100-\u017F][A-Za-zÀ-ÖØ-öø-ÿ\u0100-\u017F\-]*'
                    r'(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ\u0100-\u017F][A-Za-zÀ-ÖØ-öø-ÿ\u0100-\u017F\-]*)+$',
                    name_part
                ) and any(c.islower() for c in name_part)):
                return line

            # All-caps names (e.g. "SARAH KRISHNAMURTHY" or after stripping "DR.")
            if re.match(r'^[A-Z][A-Z\s\-]+$', name_part) and len(words) >= 2:
                return line.title()

        return None
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education_list = []
        
        # Find education section
        education_pattern = r'(?:EDUCATION|Education|ACADEMIC|Academic)\s*\n(.*?)(?=\n\s*\n[A-Z]{2,}|\Z)'
        match = re.search(education_pattern, text, re.DOTALL)
        
        if match:
            education_text = match.group(1)
        else:
            education_text = text
        
        # Extract degree information
        for degree in self.degree_keywords:
            pattern = rf'{degree}[^a-zA-Z].*?(?:\d{{4}}|\d{{2}})'
            matches = re.finditer(pattern, education_text, re.IGNORECASE | re.DOTALL)
            
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

                # Extract stream: "in Computer Science", "in Electronics & Communication", etc.
                stream_match = re.search(
                    r'\bin\s+([A-Z][A-Za-z\s&()/]+?)(?=\s+(?:from|at|of)\b|\s*,|\s*[–\-]|\s*\(|\s*\d{4}|\s*$)',
                    edu_entry, re.IGNORECASE
                )
                stream = stream_match.group(1).strip().rstrip(',') if stream_match else None

                education_list.append({
                    'degree': degree,
                    'institution': institution,
                    'year': year,
                    'stream': stream,
                    'raw_text': clean_text(edu_entry)
                })
        
        return education_list
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications, preferring a dedicated section over loose regex."""
        certifications: List[str] = []
        seen_norm: set = set()

        def _add(cert: str) -> None:
            cert = cert.strip().strip('•-–* \t')
            # Reject very short strings, bare-word noise, and anything that looks
            # like it came from a skills list (e.g. "Design Certification")
            if len(cert) < 8:
                return
            # Must contain at least two words to be a real cert name
            if len(cert.split()) < 2:
                return
            norm = re.sub(r'\s+', ' ', cert.lower())
            if norm in seen_norm:
                return
            # Reject if it is a substring of an already-added certification
            if any(norm in existing for existing in seen_norm):
                return
            # Reject if any already-added cert is a substring of the new one —
            # replace the shorter one with this more complete version
            to_remove = [ex for ex in seen_norm if ex in norm]
            for ex in to_remove:
                seen_norm.discard(ex)
                idx = next((i for i, c in enumerate(certifications)
                            if re.sub(r'\s+', ' ', c.lower()) == ex), None)
                if idx is not None:
                    certifications.pop(idx)
            seen_norm.add(norm)
            certifications.append(cert)

        # ── 1. Prefer the dedicated CERTIFICATIONS section ──────────────────
        cert_section_pattern = (
            r'(?:^|\n)[ \t]*(?:CERTIFICATIONS?|Licen[sc]es?\s*(?:&|and)\s*Certifications?|'
            r'Professional\s+Certifications?|Accreditations?)'
            r'[ \t]*\n(.*?)(?=\n[ \t]*[A-Z][A-Z\s]{2,}\n|\Z)'
        )
        sec_match = re.search(cert_section_pattern, text, re.DOTALL | re.IGNORECASE)

        if sec_match:
            section_text = sec_match.group(1)
            for line in section_text.splitlines():
                line = re.sub(r'^[\s•\-–*►▪\d\.]+', '', line).strip()
                # Strip trailing year in parens: "(2022)"
                line = re.sub(r'\s*\(\d{4}\)\s*$', '', line).strip()
                if line:
                    _add(line)

        # ── 2. Supplement with well-known cert name patterns (avoid noise) ──
        # Only add if not already captured from the section
        targeted_patterns = [
            r'(?:AWS|Azure|Microsoft|Google Cloud|GCP)\s+Certified\s+[A-Za-z][A-Za-z\s\-–]+?(?=\s*[\(\d]|\s*$|\n)',
            r'(?:PMP|CISSP|CISA|CEH|CISM|CRISC|CPA|CFA)\b',
            r'Certified\s+(?:Scrum\s+Master|Kubernetes\s+Administrator|Data\s+Scientist|'
            r'Cloud\s+Practitioner|Solutions\s+Architect|DevOps\s+Engineer|'
            r'Developer|Professional|Associate|Specialist)(?:\s*\([^\)]*\))?',
            r'(?:ITIL|Prince2|CompTIA\s+\w+)\s+(?:Foundation|Practitioner|Certified|[A-Z]\+)',
        ]
        for pattern in targeted_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                candidate = m.group(0).strip()
                # Strip trailing year in parens
                candidate = re.sub(r'\s*\(\d{4}\)\s*$', '', candidate).strip()
                _add(candidate)

        return certifications[:15]
    
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
