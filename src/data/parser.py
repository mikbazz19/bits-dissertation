"""Resume and job description parsers"""

import io
import re
from pathlib import Path
from typing import Optional, Union
import PyPDF2
import docx


class ResumeParser:
    """Parse resumes from various file formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def parse_file(self, file_path: Union[str, Path]) -> str:
        """Parse resume file and extract text"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._parse_pdf(file_path)
        elif extension == '.docx':
            return self._parse_docx(file_path)
        elif extension == '.txt':
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def parse_text(self, text: str) -> str:
        """Parse resume from text string"""
        return text.strip()
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
        
        return text.strip()
    
    def _parse_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
        
        return text.strip()
    
    def _parse_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")
        
        return text.strip()


class JobDescriptionParser:
    """Parse job descriptions from text or file"""
    
    def __init__(self):
        self.section_keywords = {
            'responsibilities': ['responsibilities', 'duties', 'role description'],
            'requirements': ['requirements', 'qualifications', 'must have'],
            'skills': ['skills', 'technical skills', 'required skills'],
            'education': ['education', 'degree', 'qualification'],
            'experience': ['experience', 'years of experience']
        }
    
    def parse_text(self, text: str) -> dict:
        """Parse job description text into structured sections"""
        text = text.strip()
        
        sections = {
            'full_text': text,
            'responsibilities': self._extract_section(text, 'responsibilities'),
            'requirements': self._extract_section(text, 'requirements'),
            'skills': self._extract_section(text, 'skills'),
            'education': self._extract_section(text, 'education'),
            'experience': self._extract_experience_requirement(text)
        }
        
        return sections
    
    def parse_file(self, file_path: Union[str, Path]) -> dict:
        """Parse job description from file"""
        file_path = Path(file_path)
        parser = ResumeParser()  # Reuse file parsing logic
        text = parser.parse_file(file_path)
        return self.parse_text(text)
    
    def _extract_section(self, text: str, section_type: str) -> str:
        """Extract specific section from job description"""
        keywords = self.section_keywords.get(section_type, [])
        
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_experience_requirement(self, text: str) -> Optional[float]:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
            r'minimum\s*(\d+)\s*(?:years?|yrs?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
