"""Tests for job matching"""

import pytest
from src.models.resume import Resume
from src.models.job import JobDescription
from src.matching.job_matcher import JobMatcher


def test_job_matching():
    """Test basic job matching"""
    matcher = JobMatcher()
    
    resume = Resume(
        raw_text="test",
        skills=['Python', 'JavaScript', 'React', 'Django'],
        total_experience_years=5.0
    )
    
    job = JobDescription(
        title="Software Engineer",
        company="TechCo",
        description="Looking for experienced developer",
        required_skills=['Python', 'JavaScript', 'React'],
        required_experience=3.0
    )
    
    result = matcher.match_resume_to_job(resume, job)
    
    assert 'overall_score' in result
    assert 'skill_score' in result
    assert 'match_level' in result
    assert result['overall_score'] > 0


def test_perfect_match():
    """Test perfect skill match"""
    matcher = JobMatcher()
    
    resume = Resume(
        raw_text="test",
        skills=['Python', 'Django', 'PostgreSQL'],
        total_experience_years=5.0
    )
    
    job = JobDescription(
        title="Backend Developer",
        company="TechCo",
        description="Backend position",
        required_skills=['Python', 'Django', 'PostgreSQL'],
        required_experience=4.0
    )
    
    result = matcher.match_resume_to_job(resume, job)
    
    assert result['skill_score'] > 90
    assert result['experience_score'] == 100
