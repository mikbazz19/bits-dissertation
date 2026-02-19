"""Tests for resume parser"""

import pytest
from src.data.parser import ResumeParser


def test_parse_text():
    """Test parsing resume from text"""
    parser = ResumeParser()
    
    sample_text = """
    John Doe
    john@email.com
    
    SKILLS
    Python, JavaScript, React
    """
    
    result = parser.parse_text(sample_text)
    assert result is not None
    assert "John Doe" in result


def test_supported_formats():
    """Test supported file formats"""
    parser = ResumeParser()
    
    assert '.pdf' in parser.supported_formats
    assert '.docx' in parser.supported_formats
    assert '.txt' in parser.supported_formats


def test_invalid_file():
    """Test handling of non-existent file"""
    parser = ResumeParser()
    
    with pytest.raises(FileNotFoundError):
        parser.parse_file("nonexistent.pdf")
