"""
Extended ground truth annotations for the final-semester evaluation.

Expands the original 2-resume evaluation set to 10 annotated resumes
with 10 resume–JD pairs, providing a more robust and convincing
benchmark for Precision / Recall / F1-Score measurement.

Resumes annotated:
  1. sample_resume_1.txt       – Jane Smith (Full Stack, 6 yr)
  2. sample_resume_2.txt       – Michael Chen (Data Scientist, 4.5 yr)
  3. resume_3_fresher.txt      – Arjun Mehta (Fresher, 0 yr)
  4. resume_5_unicode_international.txt – Vasilescu Andrei (7 yr)
  5. resume_6_career_changer.txt – Priya Raghunathan (Career Change)
  6. resume_7_overqualified.txt – Dr. Sarah Krishnamurthy (15 yr)
  7. resume_9_employment_gaps.txt – David Okonkwo (9 yr)
  8. resume_10_skills_heavy_devops.txt – Aisha Balogun (DevOps, 6 yr)
  9. resume_review_candidate.txt – Priya Sharma (ML, 3 yr)
  10. resume_repeated_skills.txt – (edge case)

Each annotation carries recruiter_decisions for at least one job,
totalling 10 unique (resume, job) evaluation pairs.
"""

from pathlib import Path
from typing import Dict, List

from .ground_truth import (
    ResumeAnnotation,
    JobAnnotation,
    ANNOTATION_RESUME_1,
    ANNOTATION_RESUME_2,
    ANNOTATION_JOB_1,
    ANNOTATION_JOB_2,
    DATA_DIR,
)


# ─────────────────────────────────────────────────────────────────────────────
# Additional Job Annotations
# ─────────────────────────────────────────────────────────────────────────────

ANNOTATION_JOB_3 = JobAnnotation(
    job_id="job_3",
    file_path=DATA_DIR / "sample_jobs" / "job_description_3_entry_level.txt",
    title="Junior Software Developer",
    required_skills=[
        "Python", "Java", "Node.js", "HTML", "CSS", "JavaScript",
        "Git",
    ],
    preferred_skills=[
        "REST API", "AWS",
    ],
    required_experience_years=0.0,
)

ANNOTATION_JOB_6 = JobAnnotation(
    job_id="job_6",
    file_path=DATA_DIR / "sample_jobs" / "job_description_6_data_analyst.txt",
    title="Data Analyst / Business Intelligence Developer",
    required_skills=[
        "SQL", "Tableau", "Python", "R",
    ],
    preferred_skills=[
        "Machine Learning", "Excel",
    ],
    required_experience_years=2.0,
)

ANNOTATION_JOB_7 = JobAnnotation(
    job_id="job_7",
    file_path=DATA_DIR / "sample_jobs" / "job_description_7_devops.txt",
    title="DevOps / Platform Engineer",
    required_skills=[
        "Kubernetes", "Terraform", "Python", "AWS",
        "Docker", "CI/CD", "Git",
    ],
    preferred_skills=[
        "Ansible", "Jenkins", "Prometheus",
    ],
    required_experience_years=4.0,
)

ANNOTATION_JOB_8 = JobAnnotation(
    job_id="job_8",
    file_path=DATA_DIR / "sample_jobs" / "job_description_8_backend_engineer.txt",
    title="Senior Backend Engineer",
    required_skills=[
        "Python", "Django", "Flask", "JavaScript", "Node.js",
        "PostgreSQL", "MySQL", "AWS", "REST API", "Git",
    ],
    preferred_skills=[
        "Microservices", "Docker", "React",
    ],
    required_experience_years=6.0,
)

ANNOTATION_JOB_9 = JobAnnotation(
    job_id="job_9",
    file_path=DATA_DIR / "sample_jobs" / "job_description_9_senior_backend.txt",
    title="Senior Software Engineer – Backend",
    required_skills=[
        "Python", "Java", "PostgreSQL", "Apache Kafka",
        "REST API", "Git", "Linux",
    ],
    preferred_skills=[
        "Kubernetes", "Spring Boot", "Django",
    ],
    required_experience_years=7.0,
)


# ─────────────────────────────────────────────────────────────────────────────
# Additional Resume Annotations
# ─────────────────────────────────────────────────────────────────────────────

ANNOTATION_RESUME_3 = ResumeAnnotation(
    resume_id="resume_3",
    file_path=DATA_DIR / "sample_resumes" / "resume_3_fresher.txt",
    name="Arjun Mehta",
    email="arjun.mehta@gmail.com",
    phone="+91-9876543210",
    skills=[
        "Python", "Java", "JavaScript", "C++",
        "HTML", "CSS", "React", "Node.js", "Express.js",
        "MySQL", "MongoDB", "Git", "Flask", "SQLite",
        "NLTK", "Scikit-learn",
    ],
    experience_entries=[
        {"title": "Software Development Intern", "company": "XYZ Technologies Pvt. Ltd."},
    ],
    total_experience_years=0.2,
    education_degrees=["Bachelor"],
    certifications=[
        "Python for Everybody",
        "AWS Cloud Practitioner Essentials",
    ],
    recruiter_decisions={
        "job_3": (72.0, True),   # Entry-level role — good fit for fresher
    },
)

ANNOTATION_RESUME_5 = ResumeAnnotation(
    resume_id="resume_5",
    file_path=DATA_DIR / "sample_resumes" / "resume_5_unicode_international.txt",
    name="Vasilescu Andrei",
    email="vasilescu.andrei@techmail.ro",
    phone="+40-721-456-789",
    skills=[
        "Java", "Python", "PHP", "JavaScript", "TypeScript",
        "Spring Boot", "Django", "Vue.js", "React",
        "Apache Kafka", "RabbitMQ",
        "PostgreSQL", "Oracle", "MongoDB", "Redis",
        "Docker", "Kubernetes", "Jenkins", "GitLab",
        "AWS", "Azure", "Microservices", "Git",
    ],
    experience_entries=[
        {"title": "Senior Software Engineer", "company": "Société Générale Global Solution Centre"},
        {"title": "Software Engineer", "company": "Orange România"},
        {"title": "Junior Developer", "company": "Freelancer"},
    ],
    total_experience_years=7.0,
    education_degrees=["Master", "Bachelor"],
    certifications=[
        "Oracle Certified Professional: Java SE 11 Developer",
        "Certified Kubernetes Administrator",
        "AWS Certified Developer",
    ],
    recruiter_decisions={
        "job_1": (75.0, True),   # Full Stack — strong Java/Python, 7 yrs
    },
)

ANNOTATION_RESUME_6 = ResumeAnnotation(
    resume_id="resume_6",
    file_path=DATA_DIR / "sample_resumes" / "resume_6_career_changer.txt",
    name="Priya Raghunathan",
    email="priya.r@careershift.com",
    phone="+1-415-222-8877",
    skills=[
        "Python", "Pandas", "NumPy", "Scikit-learn",
        "PostgreSQL", "MySQL", "SQLite",
        "Tableau", "Power BI", "Excel",
        "Git", "Statistics",
    ],
    experience_entries=[
        {"title": "Senior Marketing Manager", "company": "GlobalBrand Consumer Goods"},
        {"title": "Marketing Analyst", "company": "DigitalFirst Agency"},
    ],
    total_experience_years=4.5,
    education_degrees=["Bachelor"],
    certifications=[
        "Google Data Analytics Professional Certificate",
        "Tableau Desktop Specialist",
    ],
    recruiter_decisions={
        "job_6": (58.0, False),  # Data Analyst — career changer, borderline
    },
)

ANNOTATION_RESUME_7 = ResumeAnnotation(
    resume_id="resume_7",
    file_path=DATA_DIR / "sample_resumes" / "resume_7_overqualified.txt",
    name="Sarah Krishnamurthy",
    email="sarah.k@email.com",
    phone="+1-617-333-9900",
    skills=[
        "C++", "Python", "Go", "Java",
        "Cassandra", "Hadoop", "Spark",
        "Kubernetes", "Docker",
    ],
    experience_entries=[
        {"title": "Principal Engineer", "company": "Meta Platforms"},
        {"title": "Staff Software Engineer", "company": "Google LLC"},
        {"title": "Software Engineer II", "company": "Amazon Web Services"},
    ],
    total_experience_years=15.0,
    education_degrees=["PhD", "Master", "Bachelor"],
    certifications=[],
    recruiter_decisions={
        "job_8": (45.0, False),  # Sr Backend 6yr — massively overqualified (15yr)
    },
)

ANNOTATION_RESUME_9 = ResumeAnnotation(
    resume_id="resume_9",
    file_path=DATA_DIR / "sample_resumes" / "resume_9_employment_gaps.txt",
    name="David Okonkwo",
    email="david.okonkwo@inbox.com",
    phone="+1-646-777-3344",
    skills=[
        "Python", "Java", "JavaScript",
        "Spring Boot", "Django",
        "Apache Kafka", "PostgreSQL", "Redis",
        "AWS", "Docker", "Kubernetes",
        "Oracle", "Git",
    ],
    experience_entries=[
        {"title": "Senior Backend Engineer", "company": "FinServe Technologies"},
        {"title": "Backend Engineer", "company": "Barclays Digital"},
        {"title": "Software Developer", "company": "ClearMetrics Ltd."},
        {"title": "Junior Developer", "company": "Accenture UK"},
    ],
    total_experience_years=9.0,
    education_degrees=["Bachelor"],
    certifications=[],
    recruiter_decisions={
        "job_9": (80.0, True),   # Sr Backend 7yr — 9yr exp, Python/Java/Kafka match
    },
)

ANNOTATION_RESUME_10 = ResumeAnnotation(
    resume_id="resume_10",
    file_path=DATA_DIR / "sample_resumes" / "resume_10_skills_heavy_devops.txt",
    name="Aisha Balogun",
    email="aisha.balogun@devmail.com",
    phone="+44-7700-900123",
    skills=[
        "AWS", "GCP", "Azure",
        "Docker", "Kubernetes",
        "Terraform", "Ansible",
        "Jenkins", "GitLab",
        "Python",
        "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Apache Kafka",
        "Prometheus",
        "Git",
    ],
    experience_entries=[
        {"title": "Senior Platform Engineer", "company": "Fintech Enablers Ltd."},
        {"title": "Platform Engineer", "company": "RetailCloud UK Ltd."},
        {"title": "Junior Systems Engineer", "company": "MNO Telecom"},
    ],
    total_experience_years=6.0,
    education_degrees=["Bachelor"],
    certifications=[
        "AWS Certified DevOps Engineer",
        "Certified Kubernetes Administrator",
        "HashiCorp Certified: Terraform Associate",
        "AWS Certified Solutions Architect",
    ],
    recruiter_decisions={
        "job_7": (90.0, True),   # DevOps 4yr req — perfect match
    },
)

ANNOTATION_RESUME_REVIEW = ResumeAnnotation(
    resume_id="resume_review",
    file_path=DATA_DIR / "sample_resumes" / "resume_review_candidate.txt",
    name="Priya Sharma",
    email="priya.sharma@techmail.com",
    phone="(415) 555-2291",
    skills=[
        "Python", "PyTorch", "Spark",
        "Machine Learning", "Git", "Agile",
    ],
    experience_entries=[
        {"title": "Machine Learning Engineer", "company": "DataFlow Inc."},
        {"title": "Junior Data Scientist", "company": "InnovateLab"},
    ],
    total_experience_years=3.0,
    education_degrees=["Bachelor"],
    certifications=[
        "Google Professional Machine Learning Engineer",
    ],
    recruiter_decisions={
        "job_2": (62.0, True),   # ML Engineer 3yr — meets minimum but limited skills
    },
)


# ─────────────────────────────────────────────────────────────────────────────
# Aggregated collections for the final evaluation
# ─────────────────────────────────────────────────────────────────────────────

FINAL_RESUME_ANNOTATIONS: List[ResumeAnnotation] = [
    ANNOTATION_RESUME_1,
    ANNOTATION_RESUME_2,
    ANNOTATION_RESUME_3,
    ANNOTATION_RESUME_5,
    ANNOTATION_RESUME_6,
    ANNOTATION_RESUME_7,
    ANNOTATION_RESUME_9,
    ANNOTATION_RESUME_10,
    ANNOTATION_RESUME_REVIEW,
]

FINAL_JOB_ANNOTATIONS: List[JobAnnotation] = [
    ANNOTATION_JOB_1,
    ANNOTATION_JOB_2,
    ANNOTATION_JOB_3,
    ANNOTATION_JOB_6,
    ANNOTATION_JOB_7,
    ANNOTATION_JOB_8,
    ANNOTATION_JOB_9,
    ANNOTATION_JOB_9,
]

FINAL_JOB_ANNOTATION_MAP: Dict[str, JobAnnotation] = {
    "job_1": ANNOTATION_JOB_1,
    "job_2": ANNOTATION_JOB_2,
    "job_3": ANNOTATION_JOB_3,
    "job_6": ANNOTATION_JOB_6,
    "job_7": ANNOTATION_JOB_7,
    "job_8": ANNOTATION_JOB_8,
    "job_9": ANNOTATION_JOB_9,
}
