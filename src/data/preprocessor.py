"""Text preprocessing utilities"""

import re
from typing import List, Optional
import string

# Make spacy optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class TextPreprocessor:
    """Preprocess text for NLP tasks"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize with spaCy model (optional)"""
        self.nlp = None
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model_name)
                print(f"✓ Loaded spaCy model: {model_name}")
            except OSError:
                print(f"⚠ spaCy model '{model_name}' not found. Using regex fallbacks.")
                print(f"  To enable advanced NLP: python -m spacy download {model_name}")
        else:
            print("⚠ spaCy not installed. Using regex-based preprocessing.")
    
    def preprocess(self, text: str, 
                   lowercase: bool = True,
                   remove_punctuation: bool = False,
                   remove_stopwords: bool = False,
                   lemmatize: bool = False) -> str:
        """Preprocess text with various options"""
        
        if not text:
            return ""
        
        # Clean text
        text = self._clean_text(text)
        
        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            
            tokens = []
            for token in doc:
                # Skip stopwords if requested
                if remove_stopwords and token.is_stop:
                    continue
                
                # Skip punctuation if requested
                if remove_punctuation and token.is_punct:
                    continue
                
                # Get lemma or text
                word = token.lemma_ if lemmatize else token.text
                
                # Lowercase if requested
                if lowercase:
                    word = word.lower()
                
                tokens.append(word)
            
            return " ".join(tokens)
        else:
            # Fallback: simple regex-based preprocessing
            if lowercase:
                text = text.lower()
            
            if remove_punctuation:
                text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Simple stopword removal (basic English stopwords)
            if remove_stopwords:
                stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                           'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
                words = text.split()
                text = ' '.join([w for w in words if w.lower() not in stopwords])
            
            return text
    
    def extract_entities(self, text: str) -> dict:
        """Extract named entities from text"""
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'DATE': [],
            'WORK_OF_ART': [],
            'PRODUCT': []
        }
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
        else:
            # Fallback: regex-based extraction
            # Extract organizations (companies)
            org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Corporation|Ltd|Limited|LLC|Company|Technologies|Systems|Solutions))\b'
            entities['ORG'] = list(set(re.findall(org_pattern, text)))
            
            # Extract dates (years)
            date_pattern = r'\b((?:19|20)\d{2})\b'
            entities['DATE'] = list(set(re.findall(date_pattern, text)))
        
        return entities
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """Extract noun phrases from text"""
        if self.nlp:
            doc = self.nlp(text)
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            return noun_phrases
        else:
            # Fallback: extract capitalized phrases
            phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            return list(set(phrases))
    
    def sentence_tokenize(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
            return sentences
        else:
            # Fallback: split by period, question mark, exclamation
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing unwanted characters"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses (optional, might want to keep)
        # text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep some important ones
        # text = re.sub(r'[^a-zA-Z0-9\s\.\,\;\:\-\+\#]', '', text)
        
        return text.strip()
    
    def extract_sections(self, text: str) -> dict:
        """Extract common resume sections"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'education': r'(?:EDUCATION|Education|ACADEMIC)',
            'experience': r'(?:EXPERIENCE|Experience|WORK EXPERIENCE|Employment History)',
            'skills': r'(?:SKILLS|Skills|TECHNICAL SKILLS|Core Competencies)',
            'projects': r'(?:PROJECTS|Projects)',
            'certifications': r'(?:CERTIFICATIONS?|Certifications?|LICENSES)',
            'summary': r'(?:SUMMARY|Summary|PROFILE|Professional Summary)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(f'{pattern}[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z]|\Z)', 
                            text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
            else:
                sections[section_name] = ""
        
        return sections
