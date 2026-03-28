"""
Manually annotated ground truth for the two bundled sample resumes.

These annotations were produced by human review of:
  - data/sample_resumes/sample_resume_1.txt  (Jane Smith)
  - data/sample_resumes/sample_resume_2.txt  (Michael Chen)

Each entry is a dataclass with the ground-truth values for every extraction
target.  They serve as the reference labels when computing Precision / Recall /
F1-Score for all extraction modules.

For matching evaluation, recruiter reference decisions are also stored:
  - recruiter_score   : 0–100 normalised human rating
  - recruiter_shortlist: True if a human recruiter would shortlist the candidate
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"


# ─────────────────────────────────────────────────────────────────────────────
# Annotation schema
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResumeAnnotation:
    """Complete ground-truth annotation for one resume."""
    resume_id: str
    file_path: Path

    # Entity labels
    name:  Optional[str]
    email: Optional[str]
    phone: Optional[str]

    # Skill labels – full set of skills explicitly stated in the resume
    skills: List[str]

    # Experience labels – (job_title, company) pairs
    experience_entries: List[Dict[str, str]]

    # Total years of experience (as stated / inferred from dates)
    total_experience_years: float

    # Education labels – list of degree strings
    education_degrees: List[str]

    # Certification labels
    certifications: List[str]

    # Matching evaluation references
    # Keyed by job_id; value = (recruiter_score: float, shortlisted: bool)
    recruiter_decisions: Dict[str, tuple] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Resume 1 – Jane Smith  (sample_resume_1.txt)
# ─────────────────────────────────────────────────────────────────────────────

ANNOTATION_RESUME_1 = ResumeAnnotation(
    resume_id="resume_1",
    file_path=DATA_DIR / "sample_resumes" / "sample_resume_1.txt",

    # ── Entities ──────────────────────────────────────────────────────────
    name="Jane Smith",
    email="jane.smith@email.com",
    phone="+1 (555) 987-6543",

    # ── Skills (all skills explicitly listed in the resume) ───────────────
    skills=[
        # Programming languages
        "Python", "JavaScript", "TypeScript", "Java", "SQL",
        # Web frameworks / technologies
        "React", "Angular", "Node.js", "Django", "Flask", "Express.js",
        "HTML", "CSS", "REST API", "GraphQL",
        # Databases
        "PostgreSQL", "MongoDB", "MySQL", "Redis", "DynamoDB",
        # Cloud & DevOps
        "AWS", "Docker", "Kubernetes", "Jenkins", "CI/CD", "Git", "JIRA",
        # Other technical
        "Microservices", "Agile", "Scrum", "Unit Testing", "System Design",
        # Tools
        "VS Code", "Postman", "Selenium",
    ],

    # ── Work experience ───────────────────────────────────────────────────
    experience_entries=[
        {"title": "Senior Software Engineer", "company": "Tech Innovations Inc."},
        {"title": "Software Engineer",        "company": "Digital Solutions Corp"},
        {"title": "Junior Software Developer","company": "StartUp Labs"},
    ],

    total_experience_years=6.0,  # "6+ years" stated in summary

    # ── Education ─────────────────────────────────────────────────────────
    education_degrees=["B.Tech"],   # Bachelor of Technology in Computer Science

    # ── Certifications ────────────────────────────────────────────────────
    certifications=[
        "AWS Certified Solutions Architect - Associate",
        "Certified Scrum Master",
    ],

    # ── Recruiter decisions for known job descriptions ────────────────────
    # job_description_1.txt = Senior Full Stack Engineer at TechCorp Solutions
    recruiter_decisions={
        "job_1": (85.0, True),   # score=85, shortlisted=True
        "job_2": (40.0, False),  # score=40, shortlisted=False (ML role mismatch)
    },
)


# ─────────────────────────────────────────────────────────────────────────────
# Resume 2 – Michael Chen  (sample_resume_2.txt)
# ─────────────────────────────────────────────────────────────────────────────

ANNOTATION_RESUME_2 = ResumeAnnotation(
    resume_id="resume_2",
    file_path=DATA_DIR / "sample_resumes" / "sample_resume_2.txt",

    # ── Entities ──────────────────────────────────────────────────────────
    name="Michael Chen",
    email="michael.chen@techmail.com",
    phone="(555) 234-5678",

    # ── Skills ────────────────────────────────────────────────────────────
    skills=[
        # Programming
        "Python", "R", "SQL",
        # ML / DL
        "Scikit-learn", "TensorFlow", "PyTorch", "XGBoost",
        # Data
        "Pandas", "NumPy", "Statistics",
        # Visualisation
        "Tableau", "Matplotlib", "Seaborn",
        # Databases
        "MySQL", "PostgreSQL", "MongoDB",
        # Big Data
        "Hadoop",
        # Cloud
        "AWS",
        # Tools
        "Jupyter", "Git", "Docker",
    ],

    # ── Work experience ───────────────────────────────────────────────────
    experience_entries=[
        {"title": "Data Scientist",       "company": "Analytics Pro Solutions"},
        {"title": "Data Analyst",         "company": "Data Insights LLC"},
        {"title": "Junior Data Analyst",  "company": "StartData Corp"},
    ],

    total_experience_years=4.5,  # 2 + 1.5 + 1 years from the resume

    # ── Education ─────────────────────────────────────────────────────────
    education_degrees=["MS", "BS"],   # M.S. Data Science + B.S. Statistics

    # ── Certifications ────────────────────────────────────────────────────
    certifications=[
        "Google Data Analytics Professional Certificate",
        "TensorFlow Developer Certificate",
    ],

    # ── Recruiter decisions ───────────────────────────────────────────────
    # job_description_2.txt = Machine Learning Engineer at AI Innovations Lab
    recruiter_decisions={
        "job_1": (30.0, False),  # Full-stack role — poor fit
        "job_2": (78.0, True),   # ML Engineer role — good fit
    },
)


# ─────────────────────────────────────────────────────────────────────────────
# Job ground truth (required/preferred skills per job description)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class JobAnnotation:
    """Ground-truth annotation for one job description."""
    job_id: str
    file_path: Path
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience_years: float


ANNOTATION_JOB_1 = JobAnnotation(
    job_id="job_1",
    file_path=DATA_DIR / "sample_jobs" / "job_description_1.txt",
    title="Senior Full Stack Engineer",
    required_skills=[
        "Python", "JavaScript", "TypeScript", "React",
        "PostgreSQL", "MongoDB", "Redis",
        "AWS", "Docker", "Kubernetes",
        "REST API", "Git",
        "Node.js", "Django", "Flask",
        "HTML", "CSS",
        "Unit Testing",
    ],
    preferred_skills=[
        "Microservices", "GraphQL", "CI/CD", "Agile", "Scrum",
    ],
    required_experience_years=5.0,
)

ANNOTATION_JOB_2 = JobAnnotation(
    job_id="job_2",
    file_path=DATA_DIR / "sample_jobs" / "job_description_2.txt",
    title="Machine Learning Engineer",
    required_skills=[
        "Python", "TensorFlow", "PyTorch", "Scikit-learn",
        "Pandas", "NumPy", "SQL",
        "AWS", "Docker", "Git",
        "Statistics",
    ],
    preferred_skills=[
        "Kubernetes", "R", "Spark", "Hadoop",
        "NLP", "Computer Vision",
    ],
    required_experience_years=3.0,
)


# ─────────────────────────────────────────────────────────────────────────────
# Convenience helpers
# ─────────────────────────────────────────────────────────────────────────────

ALL_RESUME_ANNOTATIONS: List[ResumeAnnotation] = [
    ANNOTATION_RESUME_1,
    ANNOTATION_RESUME_2,
]

ALL_JOB_ANNOTATIONS: List[JobAnnotation] = [
    ANNOTATION_JOB_1,
    ANNOTATION_JOB_2,
]

RESUME_ANNOTATION_MAP: Dict[str, ResumeAnnotation] = {
    a.resume_id: a for a in ALL_RESUME_ANNOTATIONS
}

JOB_ANNOTATION_MAP: Dict[str, JobAnnotation] = {
    a.job_id: a for a in ALL_JOB_ANNOTATIONS
}
