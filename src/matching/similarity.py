"""Similarity calculation utilities"""

from typing import List, Set
import re
from difflib import SequenceMatcher


class SimilarityCalculator:
    """Calculate similarity between texts and lists"""
    
    def jaccard_similarity(self, list1: List[str], list2: List[str]) -> float:
        """Calculate Jaccard similarity coefficient"""
        if not list1 or not list2:
            return 0.0
        
        set1 = set(item.lower() for item in list1)
        set2 = set(item.lower() for item in list2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        # Simple word-based cosine similarity
        words1 = self._tokenize(text1)
        words2 = self._tokenize(text2)
        
        # Create word frequency vectors
        all_words = set(words1 + words2)
        vector1 = [words1.count(word) for word in all_words]
        vector2 = [words2.count(word) for word in all_words]
        
        # Calculate dot product and magnitudes
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def fuzzy_match(self, term: str, term_list: List[str], threshold: float = 0.8) -> List[str]:
        """Find fuzzy matches of term in term_list"""
        matches = []
        
        for item in term_list:
            similarity = self.string_similarity(term, item)
            if similarity >= threshold:
                matches.append(item)
        
        return matches
    
    def overlap_coefficient(self, list1: List[str], list2: List[str]) -> float:
        """Calculate overlap coefficient (Szymkiewicz–Simpson coefficient)"""
        if not list1 or not list2:
            return 0.0
        
        set1 = set(item.lower() for item in list1)
        set2 = set(item.lower() for item in list2)
        
        intersection = len(set1.intersection(set2))
        min_size = min(len(set1), len(set2))
        
        return intersection / min_size if min_size > 0 else 0.0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Convert to lowercase and split
        text = text.lower()
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text)
        return words
    
    def calculate_skill_relevance(self, skill: str, job_description: str) -> float:
        """Calculate how relevant a skill is to a job description"""
        # Check if skill appears in job description
        skill_lower = skill.lower()
        desc_lower = job_description.lower()
        
        if skill_lower in desc_lower:
            # Count occurrences
            count = desc_lower.count(skill_lower)
            # Normalize by length of description
            relevance = min(count / 10, 1.0)  # Cap at 1.0
            return relevance
        
        # Check for fuzzy matches
        words = self._tokenize(job_description)
        for word in words:
            if self.string_similarity(skill, word) > 0.85:
                return 0.5
        
        return 0.0
