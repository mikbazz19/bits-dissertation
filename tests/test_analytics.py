"""
Quick test script for analytics features
Run this to verify analytics modules work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.resume import Resume, Education
from src.models.job import JobDescription
from src.analysis.analytics import ScreeningAnalytics
from src.analysis.resume_quality_scorer import ResumeQualityScorer


def test_single_resume_analytics():
    """Test single resume analytics"""
    print("Testing Single Resume Analytics...")

    # Create a sample resume
    resume = Resume(
        raw_text="Sample resume text",
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-234-567-8900",
        linkedin="linkedin.com/in/johndoe",
        skills=["Python", "Java", "React", "Docker", "AWS", "MySQL", "Git"],
        total_experience_years=5.0,
        education=[Education(degree="B.Tech", institution="ABC University", year="2018", stream="Computer Science")],
        certifications=["AWS Certified Solutions Architect"]
    )

    match_result = {
        'overall_score': 78,
        'skill_score': 85,
        'experience_score': 75,
        'education_score': 70
    }

    analytics = ScreeningAnalytics()
    result = analytics.analyze_single_resume(resume, match_result)

    print(f"[OK] Profile Summary: {result['profile_summary']}")
    print(f"[OK] Total Skills: {result['total_skills']}")
    print(f"[OK] Experience Level: {result['experience_level']}")
    print(f"[OK] Strengths: {len(result['strengths'])}")
    print(f"[OK] Skills Breakdown: {len(result['skill_breakdown'])} categories")
    print()


def test_resume_quality_scorer():
    """Test resume quality scorer"""
    print("Testing Resume Quality Scorer...")

    resume = Resume(
        raw_text="Sample resume with detailed experience",
        name="Jane Smith",
        email="jane@example.com",
        phone="123-456-7890",
        linkedin="linkedin.com/in/janesmith",
        skills=["Python", "Django", "PostgreSQL", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Linux", "REST API"],
        total_experience_years=4.5,
        education=[Education(degree="M.Sc", institution="XYZ University", year="2019", stream="Data Science")],
        certifications=["AWS Certified Developer", "Kubernetes Administrator"]
    )

    scorer = ResumeQualityScorer()
    result = scorer.score_resume(resume)

    print(f"[OK] Overall Score: {result['overall_score']}/100")
    print(f"[OK] Grade: {result['grade']}")
    print(f"[OK] Component Scores:")
    for component, score in result['component_scores'].items():
        print(f"  - {component}: {score:.1f}/25")
    print(f"[OK] Strengths: {len(result['strengths'])}")
    print(f"[OK] Suggestions: {len(result['suggestions'])}")
    print()


def test_batch_analytics():
    """Test batch resume analytics"""
    print("Testing Batch Resume Analytics...")

    # Create multiple sample resumes
    resumes = [
        Resume(
            raw_text="Resume A text",
            name="Candidate A",
            email="a@example.com",
            skills=["Python", "Django", "PostgreSQL"],
            total_experience_years=3.0,
            education=[Education(degree="B.Tech", institution="Univ A", year="2020")]
        ),
        Resume(
            raw_text="Resume B text",
            name="Candidate B",
            email="b@example.com",
            skills=["Java", "Spring", "MySQL", "AWS"],
            total_experience_years=5.5,
            education=[Education(degree="M.Tech", institution="Univ B", year="2018")]
        ),
        Resume(
            raw_text="Resume C text",
            name="Candidate C",
            email="c@example.com",
            skills=["JavaScript", "React", "Node.js", "MongoDB"],
            total_experience_years=2.0,
            education=[Education(degree="B.Sc", institution="Univ C", year="2021")]
        )
    ]

    match_results = {
        0: {'overall_score': 65, 'skill_score': 70, 'decision': 'Review', 'missing_required_skills': ['Docker', 'AWS']},
        1: {'overall_score': 82, 'skill_score': 85, 'decision': 'Accept', 'missing_required_skills': ['Kubernetes']},
        2: {'overall_score': 55, 'skill_score': 60, 'decision': 'Reject', 'missing_required_skills': ['Python', 'Docker']}
    }

    analytics = ScreeningAnalytics()
    result = analytics.analyze_batch_resumes(resumes, match_results)

    print(f"[OK] Total Candidates: {result['total_candidates']}")
    print(f"[OK] Average Score: {result['score_distribution']['mean']}%")
    print(f"[OK] Decisions: {result['decisions']}")
    print(f"[OK] Experience Distribution: {result['experience_distribution']}")
    print(f"[OK] Top Skills: {len(result['top_skills'])}")
    print(f"[OK] Common Gaps: {len(result['common_missing_skills'])}")

    # Test comparison matrix
    comparison = analytics.generate_comparison_matrix(resumes, match_results)
    print(f"[OK] Comparison Matrix: {len(comparison)} rows")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Analytics Features Test Suite")
    print("=" * 60)
    print()

    try:
        test_single_resume_analytics()
        test_resume_quality_scorer()
        test_batch_analytics()

        print("=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"X Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
