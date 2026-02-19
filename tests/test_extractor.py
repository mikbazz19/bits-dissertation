"""Tests for skill extraction"""

import pytest
from src.extraction.skill_extractor import SkillExtractor


def test_skill_extraction():
    """Test basic skill extraction"""
    extractor = SkillExtractor()
    
    text = "I have experience with Python, JavaScript, React, and Django."
    skills = extractor.extract_skills(text)
    
    assert 'Python' in skills
    assert 'JavaScript' in skills
    assert 'React' in skills
    assert 'Django' in skills


def test_empty_text():
    """Test extraction from empty text"""
    extractor = SkillExtractor()
    
    skills = extractor.extract_skills("")
    assert skills == []


def test_skill_categorization():
    """Test skill categorization"""
    extractor = SkillExtractor()
    
    skills = ['Python', 'Leadership', 'React', 'Communication']
    categorized = extractor.categorize_skills(skills)
    
    assert 'technical' in categorized or 'languages' in categorized
    assert 'soft' in categorized
