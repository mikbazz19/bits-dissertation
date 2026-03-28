"""
Main entry point for the AI Resume Screening System
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config


def main():
    """Main function to run the application"""
    print("=" * 60)
    print("AI-Powered Resume Screening System")
    print("=" * 60)
    print()
    
    # Ensure directories exist
    Config.ensure_directories()
    
    print("Choose an option:")
    print("1. Run Web UI (Streamlit)")
    print("2. Run CLI Demo")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting web application...")
        print("Open your browser and go to: http://localhost:8501")
        print("\nPress Ctrl+C to stop the server")
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/app.py"])
    
    elif choice == "2":
        print("\nRunning CLI demo...")
        run_cli_demo()
    
    else:
        print("Exiting...")


def run_cli_demo():
    """Run a simple CLI demo"""
    from src.data.parser import ResumeParser, JobDescriptionParser
    from src.extraction.skill_extractor import SkillExtractor
    from src.extraction.experience_extractor import ExperienceExtractor
    from src.extraction.entity_extractor import EntityExtractor
    from src.models.resume import Resume, Education
    from src.models.job import JobDescription
    from src.matching.job_matcher import JobMatcher
    from src.analysis.gap_analyzer import GapAnalyzer
    from src.analysis.report_generator import ReportGenerator
    
    print("\n" + "=" * 60)
    print("CLI DEMO - Resume Screening")
    print("=" * 60)
    
    # Sample resume text
    sample_resume = """
    John Doe
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp
    January 2020 - Present
    - Developed scalable web applications using Python and React
    - Led a team of 5 developers
    
    Software Engineer at StartupXYZ
    June 2018 - December 2019
    - Built RESTful APIs using Django and Flask
    
    SKILLS
    Python, JavaScript, React, Django, Flask, SQL, MongoDB, AWS, Docker, Git
    
    EDUCATION
    B.Tech in Computer Science
    ABC University, 2018
    """
    
    # Sample job description
    sample_job = """
    Senior Full Stack Developer
    
    We are looking for an experienced Full Stack Developer with 5+ years of experience.
    
    Required Skills:
    - Python, JavaScript, React, Node.js
    - SQL and NoSQL databases
    - AWS cloud services
    - Docker and containerization
    - RESTful API development
    
    Preferred Skills:
    - Kubernetes, CI/CD, Microservices
    """
    
    print("\nParsing sample resume...")
    
    # Parse resume
    skill_extractor = SkillExtractor()
    experience_extractor = ExperienceExtractor()
    entity_extractor = EntityExtractor()
    
    entities = entity_extractor.extract_all_entities(sample_resume)
    skills = skill_extractor.extract_skills(sample_resume)
    experiences = experience_extractor.extract_experience(sample_resume)
    total_exp = experience_extractor.calculate_total_experience(experiences)
    
    if total_exp == 0:
        total_exp = experience_extractor.extract_experience_summary(sample_resume) or 4.0
    
    resume = Resume(
        raw_text=sample_resume,
        name=entities.get('name', 'John Doe'),
        email=entities.get('email', 'john.doe@email.com'),
        phone=entities.get('phone', '(555) 123-4567'),
        skills=skills,
        education=[],
        experience=experiences,
        total_experience_years=total_exp
    )
    
    print(f"✓ Resume parsed - {resume.name}")
    print(f"  Skills found: {len(resume.skills)}")
    print(f"  Experience: {resume.total_experience_years} years")
    
    # Parse job
    print("\nParsing job description...")
    job_skills = skill_extractor.extract_skills(sample_job)
    
    job = JobDescription(
        title="Senior Full Stack Developer",
        company="TechCompany",
        description=sample_job,
        required_skills=job_skills[:7],
        preferred_skills=job_skills[7:],
        required_experience=5.0
    )
    
    print(f"✓ Job parsed - {job.title}")
    print(f"  Required skills: {len(job.required_skills)}")
    
    # Match resume to job
    print("\nCalculating match score...")
    matcher = JobMatcher()
    match_result = matcher.match_resume_to_job(resume, job)
    
    print(f"\n{'='*60}")
    print(f"MATCH RESULTS")
    print(f"{'='*60}")
    print(f"Overall Score: {match_result['overall_score']}%")
    print(f"Match Level: {match_result['match_level']}")
    print(f"Skill Score: {match_result['skill_score']}%")
    print(f"Experience Score: {match_result['experience_score']}%")
    print(f"\nRecommendation: {match_result['recommendation']}")
    
    # Gap analysis
    print(f"\nPerforming gap analysis...")
    analyzer = GapAnalyzer()
    gap_analysis = analyzer.analyze_gaps(resume, job)
    
    print(f"\n{'='*60}")
    print(f"GAP ANALYSIS")
    print(f"{'='*60}")
    
    skill_gaps = gap_analysis['skill_gaps']
    print(f"Required Skills Coverage: {skill_gaps['required_skills_coverage']}%")
    
    if skill_gaps['missing_required_skills']:
        print(f"\nMissing Required Skills:")
        for skill in skill_gaps['missing_required_skills']:
            print(f"  - {skill}")
    
    print(f"\nImprovement Suggestions:")
    for i, suggestion in enumerate(gap_analysis['improvement_suggestions'][:3], 1):
        print(f"{i}. {suggestion}")
    
    # Generate report
    print(f"\n{'='*60}")
    report_gen = ReportGenerator()
    report = report_gen.generate_screening_report(resume, job, match_result, gap_analysis)
    
    print("\nFull report generated!")
    print("\nWould you like to see the full report? (y/n): ", end="")
    show_report = input().strip().lower()
    
    if show_report == 'y':
        print("\n")
        print(report)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()
