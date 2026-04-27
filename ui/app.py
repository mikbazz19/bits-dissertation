"""
AI-Powered Resume Screening System
Streamlit Web Application
"""

import streamlit as st
import re
import sys
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.parser import ResumeParser, JobDescriptionParser
from src.data.preprocessor import TextPreprocessor
from src.extraction.skill_extractor import SkillExtractor
from src.extraction.experience_extractor import ExperienceExtractor
from src.extraction.entity_extractor import EntityExtractor
from src.models.resume import Resume, Education, Experience
from src.models.job import JobDescription
from src.matching.job_matcher import JobMatcher
from src.analysis.gap_analyzer import GapAnalyzer
from src.analysis.report_generator import ReportGenerator
from src.analysis.analytics import ScreeningAnalytics
from src.analysis.resume_quality_scorer import ResumeQualityScorer
from src.utils.config import Config
from src.utils.email_sender import EmailSender
from src.extraction.parser import IMAGE_EXTENSIONS

# Initialize components
Config.ensure_directories()

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'resume_parsed' not in st.session_state:
        st.session_state.resume_parsed = False
    if 'job_parsed' not in st.session_state:
        st.session_state.job_parsed = False
    if 'sender_email' not in st.session_state:
        st.session_state.sender_email = ""
    if 'sender_password' not in st.session_state:
        st.session_state.sender_password = ""
    if 'smtp_port' not in st.session_state:
        st.session_state.smtp_port = 587
    if 'use_ssl' not in st.session_state:
        st.session_state.use_ssl = False
    if 'resume_file_bytes' not in st.session_state:
        st.session_state.resume_file_bytes = None
    if 'resume_file_name' not in st.session_state:
        st.session_state.resume_file_name = None
    # Batch mode state
    if 'batch_resumes_parsed' not in st.session_state:
        st.session_state.batch_resumes_parsed = False
    if 'batch_resumes' not in st.session_state:
        st.session_state.batch_resumes = []
    if 'batch_resume_errors' not in st.session_state:
        st.session_state.batch_resume_errors = {}
    if 'batch_resume_names' not in st.session_state:
        st.session_state.batch_resume_names = []
    if 'batch_resume_file_data' not in st.session_state:
        st.session_state.batch_resume_file_data = []
    if 'batch_jobs_parsed' not in st.session_state:
        st.session_state.batch_jobs_parsed = False
    if 'batch_job' not in st.session_state:
        st.session_state.batch_job = None
    if 'batch_matches_computed' not in st.session_state:
        st.session_state.batch_matches_computed = False
    if 'batch_match_results' not in st.session_state:
        st.session_state.batch_match_results = {}
    if 'batch_gaps_computed' not in st.session_state:
        st.session_state.batch_gaps_computed = False
    if 'batch_gap_analyses' not in st.session_state:
        st.session_state.batch_gap_analyses = {}
    if 'theme' not in st.session_state:
        st.session_state.theme = 'Dark'
    # Matching weights (default 50/30/20)
    if 'weight_skills' not in st.session_state:
        st.session_state.weight_skills = 50
    if 'weight_experience' not in st.session_state:
        st.session_state.weight_experience = 30
    if 'weight_education' not in st.session_state:
        st.session_state.weight_education = 20


def _apply_theme():
    """Inject CSS to apply the selected theme."""
    if st.session_state.theme == 'Light':
        st.markdown("""
        <style>
        /* ── Light theme overrides ── */
        :root {
            color-scheme: light;
        }
        /* Global background */
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background-color: #ffffff;
            color: #1a1a2e;
        }
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        [data-testid="stHeader"] {
            background-color: #ffffff;
        }

        /* Force ALL text inside main area and sidebar to dark */
        [data-testid="stAppViewContainer"] *,
        [data-testid="stSidebar"] * {
            color: #1a1a2e !important;
        }

        /* Tabs active highlight */
        [data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom-color: #4a6cf7 !important;
            color: #4a6cf7 !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
        }
        /* Expander header – keep text dark and background light on all states */
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary:hover,
        [data-testid="stExpander"] summary:focus,
        [data-testid="stExpander"] summary:active,
        [data-testid="stExpander"] > div:first-child,
        [data-testid="stExpander"] > div:first-child:hover,
        [data-testid="stExpander"] > div:first-child:focus {
            background-color: #f8f9fa !important;
            color: #1a1a2e !important;
        }
        /* Expander header SVG arrow icon */
        [data-testid="stExpander"] summary svg,
        [data-testid="stExpander"] summary:hover svg {
            fill: #1a1a2e !important;
            stroke: #1a1a2e !important;
        }

        /* Text inputs, textareas, selects – dark text on white */
        input, textarea, select {
            color: #1a1a2e !important;
            background-color: #ffffff !important;
        }
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea,
        [data-baseweb="select"] * {
            color: #1a1a2e !important;
        }
        /* Input containers – white background */
        [data-baseweb="input"],
        [data-baseweb="base-input"] {
            background-color: #ffffff !important;
            border-color: #dee2e6 !important;
        }
        /* Password toggle (eye icon) button – visible on white */
        [data-testid="stPasswordInput"] button,
        [data-baseweb="input"] button {
            color: #6c757d !important;
            background-color: #ffffff !important;
            border: none !important;
        }
        [data-testid="stPasswordInput"] button:hover,
        [data-testid="stPasswordInput"] button:focus,
        [data-baseweb="input"] button:hover,
        [data-baseweb="input"] button:focus {
            color: #6c757d !important;
            background-color: #ffffff !important;
        }
        /* Selectbox / dropdown – light background with dark text */
        [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border-color: #dee2e6 !important;
            color: #1a1a2e !important;
        }
        [data-baseweb="select"] > div:hover,
        [data-baseweb="select"] > div:focus-within {
            background-color: #ffffff !important;
            border-color: #dee2e6 !important;
        }
        /* Selectbox arrow icon */
        [data-baseweb="select"] svg {
            color: #6c757d !important;
            fill: #6c757d !important;
        }
        /* Dropdown menu (popover) */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background-color: #ffffff !important;
            color: #1a1a2e !important;
        }
        [data-baseweb="menu"] li,
        [role="option"] {
            color: #1a1a2e !important;
            background-color: #ffffff !important;
        }
        [data-baseweb="menu"] li:hover,
        [role="option"]:hover {
            background-color: #f0f2f6 !important;
            color: #1a1a2e !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] * {
            color: #1a1a2e !important;
        }
        [data-testid="stFileUploader"] section {
            background-color: #f0f2f6;
            border-color: #dee2e6;
        }

        /* Browse files button – white text on dark background */
        [data-testid="stFileUploader"] button,
        [data-testid="stFileUploaderDropzone"] button {
            color: #ffffff !important;
            background-color: #7B9BF7 !important;
            border-color: #7B9BF7 !important;
        }
        [data-testid="stFileUploader"] button:hover,
        [data-testid="stFileUploaderDropzone"] button:hover {
            color: #ffffff !important;
            background-color: #7B9BF7 !important;
            border-color: #7B9BF7 !important;
        }

        /* All action buttons – white text on blue background, stable on hover */
        .stButton button,
        .stDownloadButton button {
            color: #ffffff !important;
            background-color: #7B9BF7 !important;
            border-color: #7B9BF7 !important;
        }
        .stButton button:hover,
        .stButton button:focus,
        .stButton button:active,
        .stDownloadButton button:hover,
        .stDownloadButton button:focus,
        .stDownloadButton button:active {
            color: #ffffff !important;
            background-color: #7B9BF7 !important;
            border-color: #7B9BF7 !important;
            opacity: 1 !important;
        }
        /* Primary buttons (type="primary") – slightly deeper blue */
        .stButton button[kind="primary"],
        .stDownloadButton button[kind="primary"] {
            background-color: #6B8DF0 !important;
            border-color: #6B8DF0 !important;
            color: #ffffff !important;
        }
        .stButton button[kind="primary"]:hover,
        .stDownloadButton button[kind="primary"]:hover {
            background-color: #6B8DF0 !important;
            border-color: #6B8DF0 !important;
            color: #ffffff !important;
        }

        /* Success / error / warning / info alert boxes – keep their own text color */
        [data-testid="stAlert"] * {
            color: inherit !important;
        }

        /* Toggle / switch track */
        [data-testid="stToggle"] * {
            color: #1a1a2e !important;
        }

        /* Progress bar – green fill */
        .stProgress > div > div {
            color: #1a1a2e !important;
        }
        /* Target the filled portion of the progress bar */
        .stProgress > div > div > div > div,
        .stProgress [role="progressbar"] > div,
        .stProgress [role="progressbar"] > div > div,
        [data-testid="stProgress"] > div > div > div > div {
            background-color: #2ea043 !important;
            background-image: none !important;
        }
        /* Fallback: any deeply nested div in progress with inline width style */
        .stProgress div[style*="width:"][style*="%"] {
            background-color: #2ea043 !important;
            background-image: none !important;
        }

        /* Horizontal rules / dividers – dark line for light mode */
        hr, [data-testid="stSeparator"] {
            border-color: #1a1a2e !important;
            background-color: #1a1a2e !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        /* ── Dark theme overrides ── */
        :root {
            color-scheme: dark;
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background-color: #0e1117;
            color: #fafafa;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1a2e;
            color: #fafafa;
        }
        [data-testid="stHeader"] {
            background-color: #0e1117;
        }
        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #161b22;
            border: 1px solid #30363d;
        }
        /* Progress bar – green fill */
        .stProgress > div > div > div > div,
        .stProgress [role="progressbar"] > div,
        .stProgress [role="progressbar"] > div > div,
        [data-testid="stProgress"] > div > div > div > div {
            background-color: #2ea043 !important;
            background-image: none !important;
        }
        .stProgress div[style*="width:"][style*="%"] {
            background-color: #2ea043 !important;
            background-image: none !important;
        }
        </style>
        """, unsafe_allow_html=True)


def _detect_document_type(text: str) -> str:
    """
    Return 'resume', 'jd', or 'unknown' based on keyword scoring.
    Tolerates OCR artifacts (extra spaces before colons, etc.).
    """
    import re
    # Normalise OCR artifacts: collapse spaces around colons and multiple spaces
    lower = re.sub(r'\s*:\s*', ':', text.lower())
    lower = re.sub(r'\s+', ' ', lower)

    jd_signals = [
        r'job\s+description', r'job\s+posting', r'job\s+title', r'about\s+the\s+role',
        r'about\s+this\s+role', r'position\s+summary',
        r"we(?:\s+are|'re)\s+(?:looking|seeking|hiring)",  # "we are looking" + "we're looking"
        r'you\s+will\s+be\s+responsible', r'key\s+responsibilities',
        r'job\s+responsibilities', r'role\s+responsibilities',
        r"what\s+you'?ll\s+(?:do|work|build)", r"what\s+we'?re\s+looking\s+for",
        r'the\s+ideal\s+candidate', r'ideal\s+candidate\s+will',
        r'required\s+qualifications?', r'required\s+experience',
        r'preferred\s+qualifications?', r'preferred\s+experience',
        r'required\s+skills?', r'preferred\s+skills?',
        r'minimum\s+qualifications?', r'minimum\s+requirements?',
        r'minimum\s+\d+\s*\+?\s*years',  # "Minimum 3 years" / "Minimum 3+ years"
        r'equal\s+opportunity\s+employer', r'salary\s+range', r'compensation\s+package',
        r'benefits\s+include', r'apply\s+now', r'apply\s+today', r'apply\s+online',
        r'we\s+offer', r'what\s+you\s+bring', r'nice\s+to\s+have',
        r'join\s+our\s+team', r'we\s+are\s+hiring', r'hiring\s+for',
        r'send\s+your\s+(?:resume|cv)', r'submit\s+your\s+(?:application|resume)',
        r'company\s+overview', r'about\s+(?:the\s+)?company',
        r'location\s*:', r'job\s+location', r'work\s+location',
    ]
    resume_signals = [
        r'curriculum\s+vitae', r'professional\s+summary', r'career\s+objective',
        r'work\s+history', r'references\s+available', r'objective:',
        r'summary:', r'certifications?:', r'education:',
        # Month + year range:  "March 2021 - Present"
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\s*[-\u2013]\s*(?:present|current|\d{4})',
        # Year-only range: "2020 – Present" / "2018 – 2020"  (common in PDFs/DOCX)
        r'\b\d{4}\s*[-\u2013\u2014]\s*(?:present|current|\d{4})\b',
        r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}',   # email address
    ]

    jd_score = sum(1 for p in jd_signals if re.search(p, lower))
    resume_score = sum(1 for p in resume_signals if re.search(p, lower))

    # If JD signals are strong (3+) and outweigh resume signals, it's a JD
    if jd_score >= 3 and jd_score > resume_score:
        return 'jd'
    # If there are 2+ JD signals and no clear resume signals, likely a JD
    if jd_score >= 2 and resume_score == 0:
        return 'jd'
    # If resume signals are present and equal or more than JD signals, it's a resume
    if resume_score >= 2 and resume_score >= jd_score:
        return 'resume'
    # If there's at least 1 resume signal (email) and no strong JD signals, assume resume
    if resume_score >= 1 and jd_score < 2:
        return 'resume'
    return 'unknown'


def parse_resume(file_or_text, is_file: bool = True):
    """
    Parse a resume and return (info_dict, error_string).

    When is_file=True  : file_or_text is a Streamlit UploadedFile.
    When is_file=False : file_or_text is a plain-text string.
    """
    try:
        if not is_file:
            # ── Text input path ──
            if _detect_document_type(file_or_text) == 'jd':
                return None, "This text looks like a Job Description, not a resume. Please paste resume content here."
            from src.extraction.resume_parser import extract_resume_info
            info = extract_resume_info(file_or_text)
            return info, None

        # ── File upload path ──
        uploaded_file = file_or_text
        suffix = Path(uploaded_file.name).suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix
        ) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = Path(tmp.name)

        try:
            if suffix in IMAGE_EXTENSIONS:
                # ── OCR path: extract text AND split into sections ──
                from src.extraction.ocr_processor import OCRProcessor
                processor = OCRProcessor()
                sections  = processor.extract_sections(tmp_path)
                raw_text  = sections.pop("raw_text", "")

                if _detect_document_type(raw_text) == 'jd':
                    return None, "This file looks like a Job Description, not a resume. Please upload a resume file here."
                from src.extraction.resume_parser import extract_resume_info
                info = extract_resume_info(raw_text, ocr_sections=sections)
                return info, None

            else:
                # ── Native path: PDF / DOCX / TXT ──
                from src.extraction.parser import parse_document
                from src.extraction.resume_parser import extract_resume_info
                text = parse_document(tmp_path)
                if _detect_document_type(text) == 'jd':
                    return None, "This file looks like a Job Description, not a resume. Please upload a resume file here."
                return extract_resume_info(text), None

        finally:
            tmp_path.unlink(missing_ok=True)

    except EnvironmentError as e:
        return None, str(e)
    except ImportError as e:
        return None, f"OCR library missing: {e}"
    except Exception as e:
        return None, str(e)


def _extract_jd_role_and_company(text: str):
    """Extract job role title and company name from arbitrary JD formats."""
    import re
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return "Software Engineer", "Company"

    # Patterns that indicate metadata lines, NOT the role title
    meta_re = re.compile(
        r'^(?:company|location|department|job\s*id|date|posted|about\s+us|'
        r'website|email|phone|contact|salary|compensation|industry)\s*[:\-]',
        re.IGNORECASE
    )
    # Keywords that strongly indicate a job-role line
    role_re = re.compile(
        r'\b(?:engineer|developer|manager|analyst|scientist|consultant|designer|'
        r'architect|lead|director|specialist|intern|associate|programmer|'
        r'administrator|devops|mlops|researcher|officer|executive)\b',
        re.IGNORECASE
    )

    title = None
    company = None

    # 1. Explicit labels anywhere in first 10 lines
    for line in lines[:10]:
        if not title:
            m = re.match(r'(?:position|job\s+title|role|title)\s*[:\-]\s*(.+)', line, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
        if not company:
            m = re.match(r'company\s*[:\-]\s*(.+)', line, re.IGNORECASE)
            if m:
                company = m.group(1).strip()

    # 2. First non-metadata line that contains a role keyword
    if not title:
        for line in lines[:8]:
            if meta_re.match(line):
                continue
            if role_re.search(line) and len(line) < 100:
                # Strip trailing "| Location" noise
                title = re.split(r'\s*\|\s*', line)[0].strip()
                break

    # 3. "TechCorp | City" style second line → company
    if not company:
        for line in lines[:5]:
            if '|' in line and not role_re.search(line):
                company = line.split('|')[0].strip()
                break

    # 4. Fall back: first non-metadata, non-blank line for title
    if not title:
        for line in lines[:5]:
            if not meta_re.match(line):
                title = re.split(r'\s*\|\s*', line)[0].strip()
                break

    return (title or "Software Engineer"), (company or "Company")


def parse_job_description(text):
    """Parse job description"""
    try:
        import re
        parser = JobDescriptionParser()
        parsed = parser.parse_text(text)

        # Extract skills from requirements
        skill_extractor = SkillExtractor()
        all_skills = skill_extractor.extract_skills(text)

        # Split into required and preferred (simplified logic)
        required_skills = all_skills[:len(all_skills)//2] if len(all_skills) > 4 else all_skills
        preferred_skills = all_skills[len(all_skills)//2:] if len(all_skills) > 4 else []

        # Required experience — use parser first, then progressively broader fallbacks
        required_exp = parsed.get('experience') or 0
        if not required_exp:
            # Normalise common OCR digit/letter confusions before pattern matching
            _ocr_map = [
                (r'\bS(\s*\+?\s*(?:years?|yrs?))', r'5\1'),
                (r'\bO(\s*\+?\s*(?:years?|yrs?))', r'0\1'),
                (r'\bl(\s*\+?\s*(?:years?|yrs?))', r'1\1'),
                (r'\bI(\s*\+?\s*(?:years?|yrs?))', r'1\1'),
                (r'\bB(\s*\+?\s*(?:years?|yrs?))', r'8\1'),
            ]
            normalised_text = text
            for _pat, _rep in _ocr_map:
                normalised_text = re.sub(_pat, _rep, normalised_text, flags=re.IGNORECASE)

            exp_patterns = [
                # "5+ years of Data Engineering experience"
                r'(\d{1,2})\s*\+?\s*(?:years?|yrs?)[\s,]+of[\s,]+[\w\s]{0,60}?experience',
                # "5+ years experience" / "5+ years of experience"
                r'(\d{1,2})\s*\+?\s*(?:years?|yrs?)[\s,]+(?:of[\s,]+)?experience',
                # "experience of X years" / "experience: X years"
                r'experience[:\s]+(?:of\s+)?(\d{1,2})\s*\+?\s*(?:years?|yrs?)',
                # "at least X" / "minimum X"
                r'(?:at\s+least|minimum|min\.?)\s*(\d{1,2})\s*\+?\s*(?:years?|yrs?)',
                # range "3-5 years" — take lower bound
                r'(\d{1,2})\s*[-\u2013]\s*\d{1,2}\s*(?:years?|yrs?)',
            ]
            for pat in exp_patterns:
                m = re.search(pat, normalised_text, re.IGNORECASE)
                if m:
                    required_exp = float(m.group(1))
                    break

        # Extract role title and company
        title, company = _extract_jd_role_and_company(text)

        job = JobDescription(
            title=title,
            company=company,
            description=text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            required_experience=required_exp,
            education_requirements=[],
            responsibilities=[],
            qualifications=[]
        )

        return job, None

    except Exception as e:
        return None, str(e)


def parse_job_file(uploaded_file):
    """Parse a job description from an uploaded file and return (JobDescription, error_string)."""
    try:
        _JOB_IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}
        parser = ResumeParser()
        temp_path = Path("temp") / uploaded_file.name
        temp_path.parent.mkdir(exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            if temp_path.suffix.lower() in _JOB_IMAGE_EXTS:
                from src.extraction.ocr_processor import OCRProcessor
                ocr = OCRProcessor()
                job_text = ocr.extract_text(temp_path)
            else:
                job_text = parser.parse_file(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

        if _detect_document_type(job_text) == 'resume':
            return None, "This file looks like a Resume, not a Job Description."

        return parse_job_description(job_text)
    except Exception as e:
        return None, str(e)


def _display_parsed_resume(resume):
    """Display parsed resume information inside a Streamlit container."""
    st.write("**Personal Information:**")
    st.write(f"- Name: {resume.name or 'Not found'}")
    st.write(f"- Email: {resume.email or 'Not found'}")
    st.write(f"- Phone: {resume.phone or 'Not found'}")
    if resume.linkedin:
        _li_url = resume.linkedin if resume.linkedin.startswith(('http://', 'https://')) else 'https://' + resume.linkedin
        _li_display = re.sub(r'^https?://(www\.)?', '', _li_url).rstrip('/')
        st.markdown(f"- LinkedIn: [{_li_display}]({_li_url})")
    else:
        st.write("- LinkedIn: Not found")
    if resume.github:
        _gh_url = resume.github if resume.github.startswith(('http://', 'https://')) else 'https://' + resume.github
        _gh_display = re.sub(r'^https?://(www\.)?', '', _gh_url).rstrip('/')
        st.markdown(f"- GitHub: [{_gh_display}]({_gh_url})")
    else:
        st.write("- GitHub: Not found")
    st.write(f"- Total Experience: {resume.total_experience_years} years")

    st.write("**Skills:**")
    if resume.skills:
        st.write(", ".join(resume.skills[:20]))
    else:
        st.write("No skills detected")

    st.write("**Education:**")
    if resume.education:
        for edu in resume.education:
            degree_label = edu.degree
            if edu.stream:
                degree_label += f" in {edu.stream}"
            parts = [degree_label]
            if edu.institution:
                parts.append(edu.institution)
            if edu.year:
                parts.append(edu.year)
            st.write(f"- {', '.join(parts)}")
    else:
        st.write("No education information found")

    st.write("**Certifications:**")
    if resume.certifications:
        for cert in resume.certifications:
            st.write(f"- {cert}")
    else:
        st.write("No certifications found")

    if resume.co_curricular_activities:
        st.write("**Co-Curricular Activities:**")
        for activity in resume.co_curricular_activities:
            st.write(f"- {activity}")


def _display_parsed_job(job):
    """Display parsed job description information inside a Streamlit container."""
    st.write(f"**Title:** {job.title}")
    st.write(f"**Company:** {job.company}")
    st.write(f"**Required Experience:** {job.required_experience} years")
    st.write("**Required Skills:**")
    if job.required_skills:
        st.write(", ".join(job.required_skills))
    else:
        st.write("None identified")
    st.write("**Preferred Skills:**")
    if job.preferred_skills:
        st.write(", ".join(job.preferred_skills))
    else:
        st.write("None identified")


def _display_match_result(match_result):
    """Display match result for a single resume-JD pair."""
    _score = match_result.get('overall_score', 0)

    st.metric("Overall Match Score", f"{_score}%")

    _dec = match_result.get('decision', '')
    _reason = match_result.get('decision_reason', '')
    if _dec == "Accept":
        st.success(f"✅ **Decision: ACCEPT** — {_reason}")
    elif _dec == "Review":
        st.warning(f"🔍 **Decision: REVIEW** — {_reason}")
    else:
        st.error(f"❌ **Decision: REJECT** — {_reason}")

    # ── Fairness / borderline note ───────────────────────────────
    _near_accept = abs(_score - 75) <= 5   # within ±5 of Accept threshold
    _near_review  = abs(_score - 60) <= 5  # within ±5 of Review threshold
    if _near_accept or _near_review:
        _boundary = "Accept (75%)" if _near_accept else "Review (60%)"
        st.caption(
            f"⚖️ **Fairness Note:** Score is within 5 points of the **{_boundary}** "
            f"boundary — this borderline case warrants human review before a final decision."
        )

    hfr = match_result.get('hard_filter_results', {})
    if hfr:
        st.write("**Eligibility Check:**")
        overqualified = not hfr.get('overqualification', {}).get('passed', True)
        for key, fv in hfr.items():
            if key == 'experience' and overqualified:
                continue
            icon = "✅" if fv['passed'] else "❌"
            st.write(f"\u00a0\u00a0{icon} {fv['label']}: {fv['detail']}")

    cf = match_result.get('confidence_factor', 1.0)
    if cf < 1.0:
        st.caption(f"ℹ️ Confidence factor applied: {cf} (sparse resume data detected)")

    st.write(f"**Match Level:** {match_result['match_level']}")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Skills", f"{match_result['skill_score']}%")
    with col_b:
        st.metric("Experience", f"{match_result['experience_score']}%")
    with col_c:
        st.metric("Education", f"{match_result['education_score']}%")

    st.write("**Recommendation:**")
    st.info(match_result['recommendation'])

    if match_result.get('matched_skills'):
        st.write("**Matched Skills:**")
        st.success(", ".join(match_result['matched_skills'][:10]))

    if match_result.get('missing_required_skills'):
        st.write("**Missing Required Skills:**")
        st.error(", ".join(match_result['missing_required_skills']))

    # ── Explainability panel ─────────────────────────────────────
    with st.expander("🔍 Why this score?"):
        import pandas as pd
        _s   = match_result.get('skill_score', 0)
        _e   = match_result.get('experience_score', 0)
        _edu = match_result.get('education_score', 0)

        # Use the configured weights from session state (fall back to defaults)
        _ws  = st.session_state.get('weight_skills', 50)
        _we  = st.session_state.get('weight_experience', 30)
        _wed = st.session_state.get('weight_education', 20)

        _breakdown = pd.DataFrame({
            'Component':    ['Skills',                          'Experience',                    'Education'],
            'Score':        [f"{_s}%",                          f"{_e}%",                        f"{_edu}%"],
            'Weight':       [f"{_ws}%",                         f"{_we}%",                       f"{_wed}%"],
            'Contribution': [f"{round(_s*_ws/100,1)} pts",      f"{round(_e*_we/100,1)} pts",    f"{round(_edu*_wed/100,1)} pts"],
        })
        st.table(_breakdown)

        _raw = round(_s * _ws/100 + _e * _we/100 + _edu * _wed/100, 1)
        if cf < 1.0:
            st.write(f"**Weighted Total:** {_raw}%  ×  Confidence {cf}  =  **{_score}%**")
        else:
            st.write(f"**Weighted Total: {_score}%**")

        # Skills detail
        st.markdown("---")
        matched_req  = match_result.get('matched_skills', [])
        missing_req  = match_result.get('missing_required_skills', [])
        missing_pref = match_result.get('missing_preferred_skills', [])

        if matched_req:
            st.write(f"✅ **Matched required skills ({len(matched_req)}):** {', '.join(matched_req)}")
        if missing_req:
            st.write(f"❌ **Missing required skills ({len(missing_req)}):** {', '.join(missing_req)}")
        if missing_pref:
            st.write(f"⚠️ **Missing preferred skills ({len(missing_pref)}):** {', '.join(missing_pref[:5])}")

        # Experience & education plain text
        st.markdown("---")
        _hfr = match_result.get('hard_filter_results', {})
        if 'experience' in _hfr:
            _exp_icon = "✅" if _hfr['experience']['passed'] else "❌"
            st.write(f"{_exp_icon} **Experience:** {_hfr['experience']['detail']}")
        if 'education' in _hfr:
            _edu_icon = "✅" if _hfr['education']['passed'] else "❌"
            st.write(f"{_edu_icon} **Education:** {_hfr['education']['detail']}")


def _display_gap_analysis(gap_analysis, match_result, resume, job, ri, ji):
    """Display gap analysis for a single resume-JD pair with email provision."""
    # Skill coverage
    skill_gaps = gap_analysis['skill_gaps']
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Required Skills Coverage",
                  f"{skill_gaps['required_skills_coverage']}%")
    with col2:
        st.metric("Preferred Skills Coverage",
                  f"{skill_gaps['preferred_skills_coverage']}%")

    # Experience analysis
    st.subheader("Experience Analysis")
    exp_gaps = gap_analysis['experience_gaps']
    domain = exp_gaps.get('job_domain', 'this role')
    st.write(f"**Relevant Experience in {domain}:**")
    st.write(f"- Required: {exp_gaps['required_experience']} years")

    relevant = exp_gaps['relevant_experience']
    total = exp_gaps['total_experience']
    if relevant > 0 and relevant != total:
        st.write(f"- Candidate: {relevant} years  *(overall: {total} years)*")
    else:
        st.write(f"- Candidate: {total} years")

    _hfr = match_result.get('hard_filter_results', {})
    _overqualified = not _hfr.get('overqualification', {}).get('passed', True)
    if _overqualified:
        st.warning(f"⚠️ Overqualified: {_hfr['overqualification']['detail']}")
    elif exp_gaps['meets_requirement']:
        st.success("✅ Meets experience requirement")
    else:
        st.warning(f"⚠️ Gap: {exp_gaps['experience_gap_years']} years")

    # Improvement suggestions
    st.subheader("Improvement Recommendations")
    for idx, suggestion in enumerate(gap_analysis['improvement_suggestions'], 1):
        st.write(f"{idx}. {suggestion}")

    # Priority areas
    st.subheader("Priority Areas")
    _area_meta = {
        "Critical Skill Gaps": {
            "icon": "🔴",
            "description": "More than 3 required skills are missing.",
        },
        "Experience Requirement": {
            "icon": "🟠",
            "description": (
                f"Experience gap: "
                f"{exp_gaps.get('experience_gap_years', 0):.1f} yr(s)."
            ),
        },
        "Skill Development": {
            "icon": "🟡",
            "description": (
                f"Required-skills coverage: "
                f"{skill_gaps.get('required_skills_coverage', 0):.0f}%."
            ),
        },
        "Minor Improvements": {
            "icon": "🟢",
            "description": "Strong match. Minor refinements possible.",
        },
    }
    for area in gap_analysis['priority_areas']:
        meta = _area_meta.get(area, {"icon": "⚪", "description": area})
        st.markdown(f"{meta['icon']} **{area}** — {meta['description']}")

    # PDF report
    _pdf_key = f"batch_pdf_{ri}_{ji}"
    _pdf_state_key = f"batch_pdf_data_{ri}_{ji}"

    if st.button("📥 Generate PDF Report", key=_pdf_key):
        try:
            with st.spinner("Generating PDF..."):
                report_gen = ReportGenerator()
                pdf_buffer = report_gen.generate_pdf_report(
                    resume, job, match_result, gap_analysis
                )
                st.session_state[_pdf_state_key] = {
                    'data': pdf_buffer,
                    'file_name': (
                        f"report_{resume.name or f'candidate_{ri+1}'}"
                        f"_{job.title}"
                        f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    ),
                }
        except ImportError:
            st.error("⚠️ PDF generation requires reportlab. Install it with: pip install reportlab")
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

    if _pdf_state_key in st.session_state:
        _pdf_info = st.session_state[_pdf_state_key]
        st.download_button(
            label="💾 Download PDF",
            data=_pdf_info['data'],
            file_name=_pdf_info['file_name'],
            mime="application/pdf",
            key=f"batch_dl_{ri}_{ji}"
        )
        st.success("✅ PDF report generated successfully!")

    # Decision display
    st.markdown("---")
    overall_score = match_result.get('overall_score', 0)
    decision = match_result.get('decision', 'Reject')

    if decision == "Accept":
        st.success(f"✅ **ACCEPT** — Score {overall_score}%")
    elif decision == "Review":
        st.warning(f"🔍 **REVIEW** — Score {overall_score}%")
    else:
        reason = match_result.get('decision_reason', '')
        st.error(f"❌ **REJECT** — {reason or f'Score {overall_score}%'}")

    # ── Email section ──
    if decision in ("Accept", "Reject"):
        email_label = (
            "📧 Send Interview Invitation"
            if decision == "Accept" else
            "📧 Send Rejection Email with Gap Report"
        )
        btn_label = (
            "📤 Send Email"
            if decision == "Accept" else
            "📤 Send Rejection Email"
        )
        st.write(f"**{email_label}**")
        default_email = resume.email or ""
        recipient = st.text_input(
            "Recipient Email:",
            value=default_email,
            key=f"batch_email_to_{ri}_{ji}",
            help="One or more addresses separated by commas"
        )
        cc = st.text_input(
            "CC (optional):",
            key=f"batch_email_cc_{ri}_{ji}",
            help="One or more CC addresses separated by commas"
        )
        if st.button(btn_label, key=f"batch_send_{ri}_{ji}"):
            if not recipient.strip():
                st.error("Please enter at least one recipient email address.")
            elif not st.session_state.sender_email or not st.session_state.sender_password:
                st.error("⚠️ Please configure email settings in the sidebar first.")
            else:
                to_list = [e.strip() for e in recipient.split(',') if e.strip()]
                cc_list = [e.strip() for e in cc.split(',') if e.strip()]
                with st.spinner(f"Sending email to {', '.join(to_list)}..."):
                    try:
                        email_sender = EmailSender(
                            smtp_port=st.session_state.smtp_port,
                            use_ssl=st.session_state.use_ssl,
                            timeout=30
                        )
                        creds = dict(
                            sender_email=st.session_state.sender_email,
                            sender_password=st.session_state.sender_password,
                            cc_email=cc_list or None
                        )
                        if decision == "Accept":
                            result = email_sender.send_shortlist_email(
                                to_email=to_list,
                                candidate_name=resume.name or "Candidate",
                                company_name=job.company or "Our Company",
                                job_title=job.title or "the applied position",
                                **creds
                            )
                        else:
                            report_gen = ReportGenerator()
                            gap_report_text = report_gen.generate_gap_report(
                                gap_analysis, match_result
                            )
                            result = email_sender.send_rejection_email(
                                to_email=to_list,
                                candidate_name=resume.name or "Candidate",
                                company_name=job.company or "Our Company",
                                job_title=job.title or "the applied position",
                                gap_report=gap_report_text,
                                **creds
                            )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
                    except Exception as e:
                        st.error(f"Error sending email: {str(e)}")
    else:  # Review
        st.write("**📧 Send for Manual Review**")
        st.info(
            "Forward the candidate's resume to the hiring manager for review. "
            "A score of 60–75% requires human judgement."
        )
        review_to = st.text_input(
            "Hiring Manager Email:",
            key=f"batch_review_to_{ri}_{ji}",
            help="Hiring manager's email address"
        )
        review_cc = st.text_input(
            "CC (optional):",
            key=f"batch_review_cc_{ri}_{ji}",
            help="One or more CC addresses separated by commas"
        )
        if st.button("📤 Send Review Request", key=f"batch_review_send_{ri}_{ji}"):
            if not review_to.strip():
                st.error("Please enter the hiring manager's email.")
            elif not st.session_state.sender_email or not st.session_state.sender_password:
                st.error("⚠️ Please configure email settings in the sidebar first.")
            else:
                to_list = [e.strip() for e in review_to.split(',') if e.strip()]
                cc_list = [e.strip() for e in review_cc.split(',') if e.strip()]
                file_data = st.session_state.get('batch_resume_file_data', [])
                resume_bytes = file_data[ri][0] if ri < len(file_data) else None
                resume_fname = file_data[ri][1] if ri < len(file_data) else None
                match_summary = (
                    f"Skills: {match_result.get('skill_score', 0)}% | "
                    f"Experience: {match_result.get('experience_score', 0)}% | "
                    f"Education: {match_result.get('education_score', 0)}%"
                )
                with st.spinner("Sending review request..."):
                    try:
                        email_sender = EmailSender(
                            smtp_port=st.session_state.smtp_port,
                            use_ssl=st.session_state.use_ssl,
                            timeout=30
                        )
                        result = email_sender.send_review_email(
                            to_email=to_list,
                            candidate_name=resume.name or "Candidate",
                            company_name=job.company or "Our Company",
                            job_title=job.title or "the applied position",
                            overall_score=match_result.get('overall_score', 0),
                            sender_email=st.session_state.sender_email,
                            sender_password=st.session_state.sender_password,
                            cc_email=cc_list or None,
                            resume_bytes=resume_bytes,
                            resume_filename=resume_fname,
                            match_summary=match_summary
                        )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
                    except Exception as e:
                        st.error(f"Error sending email: {str(e)}")


def _render_batch_mode(tab1, tab2, tab3, tab4):
    """Render the batch-processing mode UI (multiple resumes vs one JD)."""

    # ── Tab 1: Batch Resume Analysis ──────────────────────────────
    with tab1:
        st.header("Batch Resume Analysis")

        uploaded_files = st.file_uploader(
            "Upload Resumes (max 10)",
            type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'],
            accept_multiple_files=True,
            key="batch_resume_files"
        )

        # Clear batch state when files are removed
        if not uploaded_files and st.session_state.batch_resumes_parsed:
            st.session_state.batch_resumes_parsed = False
            st.session_state.batch_resumes = []
            st.session_state.batch_resume_errors = {}
            st.session_state.batch_resume_names = []
            st.session_state.batch_resume_file_data = []
            st.session_state.batch_matches_computed = False
            st.session_state.batch_match_results = {}
            st.session_state.batch_gaps_computed = False
            st.session_state.batch_gap_analyses = {}

        if uploaded_files:
            if len(uploaded_files) > 10:
                st.error("⚠️ Maximum 10 resumes allowed. Please remove some files.")
            else:
                st.info(f"📁 {len(uploaded_files)} resume(s) selected")

                if st.button("Parse All Resumes", key="batch_parse_resumes"):
                    resumes = []
                    errors = {}
                    names = []
                    file_data = []

                    progress = st.progress(0, text="Parsing resumes...")
                    for i, f in enumerate(uploaded_files):
                        names.append(f.name)
                        file_bytes = f.getvalue()
                        file_data.append((file_bytes, f.name))
                        # Seek back to start so parse_resume can read() the file
                        f.seek(0)
                        resume, error = parse_resume(f, is_file=True)
                        if error:
                            resumes.append(None)
                            errors[i] = error
                        else:
                            resumes.append(resume)
                        progress.progress(
                            (i + 1) / len(uploaded_files),
                            text=f"Parsed {i + 1}/{len(uploaded_files)}..."
                        )

                    st.session_state.batch_resumes = resumes
                    st.session_state.batch_resume_errors = errors
                    st.session_state.batch_resume_names = names
                    st.session_state.batch_resume_file_data = file_data
                    st.session_state.batch_resumes_parsed = True
                    # Reset downstream results
                    st.session_state.batch_matches_computed = False
                    st.session_state.batch_match_results = {}
                    st.session_state.batch_gaps_computed = False
                    st.session_state.batch_gap_analyses = {}

                    ok = sum(1 for r in resumes if r is not None)
                    st.success(f"✅ {ok}/{len(uploaded_files)} resumes parsed successfully!")

        # Display parsed resumes in collapsible sections
        if st.session_state.batch_resumes_parsed:
            st.markdown("---")
            st.subheader("Parsed Resumes")
            for i, resume in enumerate(st.session_state.batch_resumes):
                name = st.session_state.batch_resume_names[i]
                if resume is None:
                    with st.expander(f"❌ Resume {i+1}: {name} — Parse Error"):
                        st.error(st.session_state.batch_resume_errors.get(i, "Unknown error"))
                else:
                    label = f"✅ Resume {i+1}: {resume.name or name}"
                    with st.expander(label):
                        _display_parsed_resume(resume)

    # ── Tab 2: Job Matching (one JD vs all resumes) ───────────────
    with tab2:
        st.header("Job Matching — One JD vs All Resumes")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Job Description")
            jd_input_type = st.radio(
                "Job Input Method:", ["Upload File", "Paste Text"],
                key="batch_jd_input"
            )

            if jd_input_type == "Upload File":
                uploaded_jd_file = st.file_uploader(
                    "Upload Job Description (PDF, DOCX, TXT, or Image)",
                    type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'],
                    key="batch_jd_file"
                )

                # Clear JD state when file removed
                if uploaded_jd_file is None and st.session_state.batch_jobs_parsed:
                    st.session_state.batch_jobs_parsed = False
                    st.session_state.batch_job = None
                    st.session_state.batch_matches_computed = False
                    st.session_state.batch_match_results = {}
                    st.session_state.batch_gaps_computed = False
                    st.session_state.batch_gap_analyses = {}

                if uploaded_jd_file:
                    _ext = Path(uploaded_jd_file.name).suffix.lower()
                    if _ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'}:
                        st.info("🖼️ Image file detected — OCR will extract text automatically.")

                if uploaded_jd_file and st.button("Parse Job Description", key="batch_parse_jd"):
                    with st.spinner("Parsing job description..."):
                        job, error = parse_job_file(uploaded_jd_file)
                        if error:
                            st.error(error)
                        else:
                            st.session_state.batch_job = job
                            st.session_state.batch_jobs_parsed = True
                            st.session_state.batch_matches_computed = False
                            st.session_state.batch_match_results = {}
                            st.session_state.batch_gaps_computed = False
                            st.session_state.batch_gap_analyses = {}
                            st.success("✅ Job description parsed!")
            else:
                jd_text = st.text_area(
                    "Enter Job Description:", height=300, key="batch_jd_text"
                )

                # Clear JD state when text removed
                if not jd_text and st.session_state.batch_jobs_parsed:
                    st.session_state.batch_jobs_parsed = False
                    st.session_state.batch_job = None
                    st.session_state.batch_matches_computed = False
                    st.session_state.batch_match_results = {}
                    st.session_state.batch_gaps_computed = False
                    st.session_state.batch_gap_analyses = {}

                if jd_text and st.button("Parse Job Description", key="batch_parse_jd"):
                    if _detect_document_type(jd_text) == 'resume':
                        st.error(
                            "This text looks like a Resume, not a Job Description. "
                            "Please paste JD content here."
                        )
                    else:
                        job, error = parse_job_description(jd_text)
                        if error:
                            st.error(f"Error: {error}")
                        else:
                            st.session_state.batch_job = job
                            st.session_state.batch_jobs_parsed = True
                            st.session_state.batch_matches_computed = False
                            st.session_state.batch_match_results = {}
                            st.session_state.batch_gaps_computed = False
                            st.session_state.batch_gap_analyses = {}
                            st.success("✅ Job description parsed!")

            # Show parsed JD summary
            if st.session_state.batch_jobs_parsed and st.session_state.batch_job:
                st.markdown("---")
                st.write("**Parsed JD Summary:**")
                _display_parsed_job(st.session_state.batch_job)

        with col2:
            st.subheader("Match Results")

            if (st.session_state.batch_resumes_parsed and
                    st.session_state.batch_jobs_parsed):

                valid_resumes = [
                    (i, r) for i, r in enumerate(st.session_state.batch_resumes)
                    if r is not None
                ]
                job = st.session_state.batch_job

                if not valid_resumes:
                    st.warning("No valid resumes to match. Please fix resume parsing errors first.")
                else:
                    st.info(
                        f"Ready to match **{len(valid_resumes)}** resume(s) "
                        f"against **{job.title}**"
                    )

                    if st.button("Calculate Match Scores", key="batch_calc_matches"):
                        match_results = {}
                        matcher = JobMatcher(
                            skill_weight=st.session_state.weight_skills / 100,
                            experience_weight=st.session_state.weight_experience / 100,
                            education_weight=st.session_state.weight_education / 100,
                        )
                        total = len(valid_resumes)
                        progress = st.progress(0, text="Computing matches...")

                        for idx, (ri, resume) in enumerate(valid_resumes):
                            match_result = matcher.match_resume_to_job(resume, job)
                            match_results[ri] = match_result
                            progress.progress(
                                (idx + 1) / total,
                                text=f"Matched {idx + 1}/{total}..."
                            )

                        st.session_state.batch_match_results = match_results
                        st.session_state.batch_matches_computed = True
                        st.session_state.batch_gaps_computed = False
                        st.session_state.batch_gap_analyses = {}
                        st.success(f"✅ {total} match score(s) computed!")

                # Display match results in collapsible sections
                if st.session_state.batch_matches_computed:
                    st.markdown("---")

                    # ── Ranked Leaderboard ────────────────────────────────
                    _medal = {0: "🥇", 1: "🥈", 2: "🥉"}
                    _ranked = sorted(
                        st.session_state.batch_match_results.items(),
                        key=lambda x: x[1]['overall_score'],
                        reverse=True
                    )
                    st.write("**🏆 Candidate Ranking:**")
                    for _rank, (_ri, _mr) in enumerate(_ranked):
                        _rname = (st.session_state.batch_resumes[_ri].name
                                  or st.session_state.batch_resume_names[_ri])
                        _rscore = _mr['overall_score']
                        _rdec   = _mr.get('decision', '')
                        _rdec_icon = {"Accept": "✅", "Review": "🔍"}.get(_rdec, "❌")
                        _rank_label = _medal.get(_rank, f"#{_rank + 1}")
                        st.write(f"{_rank_label} &nbsp; **{_rname}** — {_rscore}% &nbsp; {_rdec_icon} {_rdec}")
                    st.markdown("---")

                    for ri, m_result in st.session_state.batch_match_results.items():
                        resume = st.session_state.batch_resumes[ri]
                        r_name = resume.name or st.session_state.batch_resume_names[ri]
                        score = m_result['overall_score']
                        decision = m_result.get('decision', '')
                        icon = {"Accept": "✅", "Review": "🔍"}.get(decision, "❌")
                        label = f"{icon} {r_name} — {score}% ({decision})"
                        with st.expander(label):
                            _display_match_result(m_result)
            else:
                st.info(
                    "Please parse resumes (Resume Analysis tab) and "
                    "a job description (left panel) to perform matching."
                )

    # ── Tab 3: Batch Gap Analysis ─────────────────────────────────
    with tab3:
        st.header("Batch Gap Analysis")

        if not st.session_state.batch_matches_computed:
            st.info(
                "Please complete batch resume parsing, JD parsing, and "
                "match score calculation first."
            )
        else:
            if st.button("Generate All Gap Analyses", key="batch_gen_gaps"):
                gap_analyses = {}
                match_results = st.session_state.batch_match_results
                job = st.session_state.batch_job
                analyzer = GapAnalyzer()

                total = len(match_results)
                progress = st.progress(0, text="Generating gap analyses...")
                done = 0

                for ri in match_results:
                    resume = st.session_state.batch_resumes[ri]
                    gap = analyzer.analyze_gaps(resume, job)
                    gap_analyses[ri] = gap
                    done += 1
                    progress.progress(
                        done / total,
                        text=f"Analyzed {done}/{total}..."
                    )

                st.session_state.batch_gap_analyses = gap_analyses
                st.session_state.batch_gaps_computed = True
                st.success(f"✅ {total} gap analysis report(s) generated!")

            if st.session_state.batch_gaps_computed:
                st.markdown("---")
                job = st.session_state.batch_job
                for ri, gap in st.session_state.batch_gap_analyses.items():
                    resume = st.session_state.batch_resumes[ri]
                    m_result = st.session_state.batch_match_results[ri]
                    r_name = resume.name or st.session_state.batch_resume_names[ri]
                    label = f"📊 {r_name} vs {job.title}"
                    # Keep expander open if user generated a PDF inside it
                    _is_expanded = f"batch_pdf_data_{ri}_0" in st.session_state
                    with st.expander(label, expanded=_is_expanded):
                        _display_gap_analysis(gap, m_result, resume, job, ri, 0)

    # ── Tab 4: Analytics (Batch Mode) ─────────────────────────────
    with tab4:
        st.header("📈 Batch Analytics & Insights")

        if not st.session_state.batch_matches_computed:
            st.info("Please complete batch resume parsing, JD parsing, and match score calculation to view analytics.")
        else:
            analytics = ScreeningAnalytics()
            resumes = st.session_state.batch_resumes
            match_results = st.session_state.batch_match_results

            # Generate analytics
            batch_analytics = analytics.analyze_batch_resumes(resumes, match_results)

            if 'error' in batch_analytics:
                st.error(batch_analytics['error'])
            else:
                import plotly.graph_objects as go
                # Determine chart template and font color based on current theme
                _is_light = st.session_state.get('theme', 'Dark') == 'Light'
                _chart_template = 'plotly' if _is_light else 'plotly_dark'
                _chart_font_color = '#111111' if _is_light else '#f0f2f6'
                _axis_cfg = dict(
                    tickfont=dict(color=_chart_font_color),
                    title=dict(font=dict(color=_chart_font_color))
                )

                # Overview metrics
                st.subheader("📊 Overview")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Candidates", batch_analytics['total_candidates'])
                with col2:
                    st.metric("Avg Score", f"{batch_analytics['score_distribution']['mean']}%")
                with col3:
                    st.metric("Accepted", batch_analytics['decisions'].get('Accept', 0))
                with col4:
                    st.metric("Rejected", batch_analytics['decisions'].get('Reject', 0))

                st.markdown("---")

                # Two column layout for visualizations
                col_left, col_right = st.columns(2)

                with col_left:
                    # Score Distribution
                    st.subheader("📈 Score Distribution")
                    scores = batch_analytics['score_distribution']['scores']
                    if scores:
                        fig = go.Figure(data=[go.Histogram(
                            x=scores,
                            nbinsx=10,
                            marker_color='#4a6cf7',
                            opacity=0.75
                        )])
                        fig.update_layout(
                            template=_chart_template,
                            xaxis_title="Match Score (%)",
                            yaxis_title="Number of Candidates",
                            height=300,
                            margin=dict(l=20, r=20, t=30, b=20),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color=_chart_font_color),
                            xaxis=_axis_cfg,
                            yaxis=_axis_cfg
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Score statistics
                        st.write("**Statistics:**")
                        stat_col1, stat_col2 = st.columns(2)
                        with stat_col1:
                            st.write(f"Mean: {batch_analytics['score_distribution']['mean']}%")
                            st.write(f"Min: {batch_analytics['score_distribution']['min']}%")
                        with stat_col2:
                            st.write(f"Median: {batch_analytics['score_distribution']['median']}%")
                            st.write(f"Max: {batch_analytics['score_distribution']['max']}%")

                    # Decision Breakdown
                    st.subheader("✅ Decision Breakdown")
                    decisions = batch_analytics['decisions']
                    if any(decisions.values()):
                        fig = go.Figure(data=[go.Pie(
                            labels=list(decisions.keys()),
                            values=list(decisions.values()),
                            marker=dict(colors=['#2ea043', '#f59f00', '#d73a49']),
                            hole=0.4,
                            textfont=dict(color=_chart_font_color)
                        )])
                        fig.update_layout(
                            template=_chart_template,
                            height=300,
                            margin=dict(l=20, r=20, t=30, b=20),
                            showlegend=True,
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color=_chart_font_color),
                            legend=dict(font=dict(color=_chart_font_color))
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col_right:
                    # Experience Distribution
                    st.subheader("💼 Experience Distribution")
                    exp_dist = batch_analytics['experience_distribution']
                    if any(exp_dist.values()):
                        fig = go.Figure(data=[go.Bar(
                            x=list(exp_dist.keys()),
                            y=list(exp_dist.values()),
                            marker_color=['#34d399', '#60a5fa', '#a78bfa'],
                            text=list(exp_dist.values()),
                            textposition='auto',
                            textfont=dict(color=_chart_font_color)
                        )])
                        fig.update_layout(
                            template=_chart_template,
                            xaxis_title="Experience Level",
                            yaxis_title="Count",
                            height=300,
                            margin=dict(l=20, r=20, t=30, b=20),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            showlegend=False,
                            font=dict(color=_chart_font_color),
                            xaxis=_axis_cfg,
                            yaxis=_axis_cfg
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Experience statistics
                        st.write("**Experience Statistics:**")
                        exp_stats = batch_analytics['experience_stats']
                        stat_col1, stat_col2 = st.columns(2)
                        with stat_col1:
                            st.write(f"Mean: {exp_stats['mean']} years")
                            st.write(f"Min: {exp_stats['min']} years")
                        with stat_col2:
                            st.write(f"Median: {exp_stats['median']} years")
                            st.write(f"Max: {exp_stats['max']} years")

                    # Top Skills
                    st.subheader("🔥 Most Common Skills")
                    top_skills = batch_analytics['top_skills']
                    if top_skills:
                        for idx, (skill, count) in enumerate(top_skills[:8], 1):
                            st.write(f"{idx}. **{skill.title()}** — {count} candidate(s)")

                # Comparison Table
                st.markdown("---")
                st.subheader("📋 Candidate Comparison Table")
                comparison_data = analytics.generate_comparison_matrix(resumes, match_results)

                if comparison_data:
                    # Create dataframe for display
                    import pandas as pd
                    df = pd.DataFrame(comparison_data)
                    df_display = df[[
                        'name', 'experience', 'skills_count', 'overall_score',
                        'skill_score', 'experience_score', 'education_score',
                        'decision', 'certifications'
                    ]]
                    df_display.columns = [
                        'Name', 'Exp (yrs)', 'Skills', 'Overall %',
                        'Skill %', 'Exp %', 'Edu %', 'Decision', 'Certs'
                    ]

                    # Color code by decision
                    def color_decision(val):
                        if val == 'Accept':
                            return 'background-color: #1a7f37; color: #ffffff'
                        elif val == 'Review':
                            return 'background-color: #b8860b; color: #ffffff'
                        elif val == 'Reject':
                            return 'background-color: #b91c1c; color: #ffffff'
                        return ''

                    styled_df = df_display.style.applymap(color_decision, subset=['Decision'])
                    st.dataframe(styled_df, use_container_width=True, height=400)

                    # Export to CSV
                    csv = df_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Comparison Table (CSV)",
                        data=csv,
                        file_name=f"candidate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

                # Common Gaps
                if batch_analytics.get('common_missing_skills'):
                    st.markdown("---")
                    st.subheader("🎯 Common Skill Gaps")
                    st.write("Skills most frequently missing across candidates:")
                    common_gaps = batch_analytics['common_missing_skills']
                    for idx, (skill, count) in enumerate(common_gaps[:10], 1):
                        percentage = (count / batch_analytics['total_candidates']) * 100
                        st.write(f"{idx}. **{skill.title()}** — missing in {count} candidates ({percentage:.0f}%)")


def _render_sidebar():
    """Render the sidebar (shared by Single and Batch modes)."""
    with st.sidebar:
        # ── Theme toggle at the very top ──
        st.toggle(
            "☀️ Light Mode" if st.session_state.theme == 'Dark' else "🌙 Dark Mode",
            value=(st.session_state.theme == 'Light'),
            key="_theme_toggle",
            on_change=lambda: st.session_state.update(
                theme='Light' if st.session_state._theme_toggle else 'Dark'
            ),
            help="Switch between Light and Dark themes"
        )
        st.markdown("---")

        # ── 1. About ─────────────────────────────────────────────
        with st.expander("ℹ️ About", expanded=False):
            st.write("""
            This AI-powered system helps automate resume screening by:
            - Parsing resumes in multiple formats (PDF, DOCX, TXT)
            - **OCR support** for image & scanned resumes (PNG, JPG, TIFF, BMP)
            - Extracting skills, experience, and qualifications
            - Matching candidates with job requirements
            - Identifying skill gaps
            - Providing actionable feedback
            - Emailing gap analysis reports
            """)

        # ── 2. How to Use ────────────────────────────────────────
        with st.expander("📖 How to Use", expanded=False):
            st.write("""
            1. **Resume Analysis**: Upload or paste a resume (PDF/DOCX/TXT or image)
            2. **Job Matching**: Upload or enter a job description (same formats)
            3. **Gap Analysis**: View detailed skill gaps and improvement suggestions

            *Image files (PNG, JPG, TIFF, BMP) are processed via OCR automatically.*
            """)

        st.markdown("---")

        # ── 3. Matching Weights ───────────────────────────────────
        with st.expander("⚖️ Matching Weights", expanded=True):
            st.caption("Adjust how each component contributes to the overall score. All three must sum to exactly 100%.")

            _w_skills = st.slider(
                "Skills weight (%)", min_value=0, max_value=100,
                value=st.session_state.weight_skills, step=5, key="_ws"
            )
            _w_exp = st.slider(
                "Experience weight (%)", min_value=0, max_value=100,
                value=st.session_state.weight_experience, step=5, key="_we"
            )
            _w_edu = st.slider(
                "Education weight (%)", min_value=0, max_value=100,
                value=st.session_state.weight_education, step=5, key="_wed"
            )

            _w_total = _w_skills + _w_exp + _w_edu

            if _w_total > 100:
                st.error(f"⚠️ Weights sum to {_w_total}% — exceeds 100%. Please reduce them.")
                _weights_valid = False
            elif _w_total < 100:
                st.warning(f"⚠️ Weights sum to {_w_total}% — must equal 100%. Please increase them.")
                _weights_valid = False
            else:
                st.success(f"✅ Weights sum to 100% — Skills {_w_skills}% · Exp {_w_exp}% · Edu {_w_edu}%")
                _weights_valid = True

            if _weights_valid and (
                _w_skills != st.session_state.weight_skills
                or _w_exp != st.session_state.weight_experience
                or _w_edu != st.session_state.weight_education
            ):
                st.session_state.weight_skills = _w_skills
                st.session_state.weight_experience = _w_exp
                st.session_state.weight_education = _w_edu
                # Invalidate existing match results so user re-runs with new weights
                st.session_state.batch_matches_computed = False
                st.session_state.batch_match_results = {}
                st.session_state.batch_gaps_computed = False
                st.session_state.batch_gap_analyses = {}
                if 'match_result' in st.session_state:
                    del st.session_state['match_result']

        st.markdown("---")

        # ── 4. Email Configuration ───────────────────────────────
        with st.expander("📧 Email Configuration", expanded=False):
            st.info("Configure your email settings to send gap analysis reports to candidates.")

            sender_email = st.text_input(
                "Sender Email",
                value=st.session_state.sender_email,
                type="default",
                placeholder="your-email@gmail.com",
                help="Email address to send from"
            )

            sender_password = st.text_input(
                label="Password/App Password",
                value=st.session_state.sender_password,
                type="password"
            )
            st.write("**SMTP Configuration**")
            col1, col2 = st.columns(2)
            with col1:
                smtp_option = st.selectbox(
                    "Connection Type",
                    options=["Port 587 (TLS)", "Port 465 (SSL)"],
                    index=0 if st.session_state.smtp_port == 587 else 1,
                    help="Try Port 465 (SSL) if Port 587 fails due to firewall/network issues"
                )

            with col2:
                if smtp_option == "Port 587 (TLS)":
                    st.session_state.smtp_port = 587
                    st.session_state.use_ssl = False
                else:
                    st.session_state.smtp_port = 465
                    st.session_state.use_ssl = True

                st.metric("Port", st.session_state.smtp_port)

            col_save, col_test = st.columns(2)
            with col_save:
                if st.button("💾 Save Config", use_container_width=True):
                    st.session_state.sender_email = sender_email
                    st.session_state.sender_password = sender_password
                    st.success("✅ Configuration saved!")

            with col_test:
                if st.button("🔌 Test Connection", use_container_width=True):
                    if not sender_email or not sender_password:
                        st.error("Please enter email and password first")
                    else:
                        with st.spinner("Testing connection..."):
                            email_sender = EmailSender(
                                smtp_port=st.session_state.smtp_port,
                                use_ssl=st.session_state.use_ssl,
                                timeout=30
                            )
                            result = email_sender.test_connection(sender_email, sender_password)
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.session_state.sender_email = sender_email
                                st.session_state.sender_password = sender_password
                            else:
                                st.error(f"❌ {result['message']}")

            with st.expander("ℹ️ Gmail Setup Instructions"):
                st.write("""
                **For Gmail users:**
                1. Go to your Google Account settings
                2. Enable 2-Step Verification
                3. Go to Security > 2-Step Verification > App passwords
                4. Generate a new app password
                5. Use that password here (not your regular Gmail password)

                **If connection fails (WinError 10060):**
                - Try switching to Port 465 (SSL)
                - Check Windows Firewall settings
                - Temporarily disable antivirus
                - Try from a different network
                - Some ISPs block SMTP ports
                """)

            with st.expander("🔧 Troubleshooting"):
                st.write("""
                **Common Issues:**

                1. **Connection Timeout (WinError 10060)**
                   - Your firewall/antivirus may be blocking the connection
                   - Try Port 465 (SSL) instead of Port 587 (TLS)
                   - Check if your ISP blocks SMTP ports

                2. **Authentication Failed**
                   - Use App Password, not regular password for Gmail
                   - Ensure 2-Step Verification is enabled

                3. **Still not working?**
                   - Try from a different network (mobile hotspot)
                   - Check Windows Defender Firewall settings
                   - Contact your IT department if on corporate network
                """)


def main():
    """Main application"""
    initialize_session_state()
    _apply_theme()
    
    st.title("🤖 AI-Powered Resume Screening System")
    st.markdown("### Intelligent Resume Analysis and Job Matching")

    st.markdown("---")

    # Tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Resume Analysis", "🔍 Job Matching", "📊 Gap Analysis", "📈 Analytics"])

    # ── Mode selector inside Resume tab ──
    with tab1:
        mode = st.radio(
            "Processing Mode:",
            ["Single", "Batch"],
            horizontal=True,
            key="processing_mode",
            help="Single: one resume, one JD.  Batch: up to 10 resumes against one JD."
        )
        st.markdown("---")

    if mode == "Batch":
        _render_batch_mode(tab1, tab2, tab3, tab4)
        _render_sidebar()
        return

    # ═══════════════════════════════════════════════════════════════
    #  SINGLE MODE — original flow (unchanged)
    # ═══════════════════════════════════════════════════════════════

    # Tab 1: Resume Analysis
    with tab1:
        st.header("Resume Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Upload Resume")
            upload_type = st.radio("Input Method:", ["Upload File", "Paste Text"])
            
            resume = None
            if upload_type == "Upload File":
                uploaded_file = st.file_uploader(
                    "Upload Resume (PDF, DOCX, TXT, or Image)",
                    type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp']
                )

                # Clear parsed data when user removes the file
                if uploaded_file is None and st.session_state.resume_parsed:
                    st.session_state.resume_parsed = False
                    st.session_state.pop('resume', None)

                if uploaded_file:
                    _ext = Path(uploaded_file.name).suffix.lower()
                    if _ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'}:
                        st.info("🖼️ Image file detected — OCR will extract text automatically.")
                
                if uploaded_file and st.button("Parse Resume"):
                    st.session_state.resume_file_bytes = uploaded_file.getvalue()
                    st.session_state.resume_file_name = uploaded_file.name
                    with st.spinner("Parsing resume..."):
                        resume, error = parse_resume(uploaded_file, is_file=True)
                        
                        if error:
                            st.error(error)
                        else:
                            st.session_state.resume = resume
                            st.session_state.resume_parsed = True
                            st.success("✅ Resume parsed successfully!")
            else:
                resume_text = st.text_area("Paste Resume Text:", height=300)

                # Clear parsed data when user clears the text area
                if not resume_text and st.session_state.resume_parsed:
                    st.session_state.resume_parsed = False
                    st.session_state.pop('resume', None)
                
                if resume_text and st.button("Parse Resume"):
                    st.session_state.resume_file_bytes = None
                    st.session_state.resume_file_name = None
                    with st.spinner("Parsing resume..."):
                        resume, error = parse_resume(resume_text, is_file=False)
                        
                        if error:
                            st.error(error)
                        else:
                            st.session_state.resume = resume
                            st.session_state.resume_parsed = True
                            st.success("✅ Resume parsed successfully!")
        
        with col2:
            st.subheader("Parsed Information")
            
            if st.session_state.resume_parsed:
                resume = st.session_state.resume
                
                st.write("**Personal Information:**")
                st.write(f"- Name: {resume.name or 'Not found'}")
                st.write(f"- Email: {resume.email or 'Not found'}")
                st.write(f"- Phone: {resume.phone or 'Not found'}")
                if resume.linkedin:
                    _li_url = resume.linkedin if resume.linkedin.startswith(('http://', 'https://')) else 'https://' + resume.linkedin
                    _li_display = re.sub(r'^https?://(www\.)?', '', _li_url).rstrip('/')
                    st.markdown(f"- LinkedIn: [{_li_display}]({_li_url})")
                else:
                    st.write("- LinkedIn: Not found")
                if resume.github:
                    _gh_url = resume.github if resume.github.startswith(('http://', 'https://')) else 'https://' + resume.github
                    _gh_display = re.sub(r'^https?://(www\.)?', '', _gh_url).rstrip('/')
                    st.markdown(f"- GitHub: [{_gh_display}]({_gh_url})")
                else:
                    st.write("- GitHub: Not found")
                st.write(f"- Total Experience: {resume.total_experience_years} years")
                
                st.write("**Skills:**")
                if resume.skills:
                    st.write(", ".join(resume.skills[:20]))
                else:
                    st.write("No skills detected")
                
                st.write("**Education:**")
                if resume.education:
                    for edu in resume.education:
                        degree_label = edu.degree
                        if edu.stream:
                            degree_label += f" in {edu.stream}"
                        parts = [degree_label]
                        if edu.institution:
                            parts.append(edu.institution)
                        if edu.year:
                            parts.append(edu.year)
                        st.write(f"- {', '.join(parts)}")
                else:
                    st.write("No education information found")
                
                st.write("**Certifications:**")
                if resume.certifications:
                    for cert in resume.certifications:
                        st.write(f"- {cert}")
                else:
                    st.write("No certifications found")

                if resume.co_curricular_activities:
                    st.write("**Co-Curricular Activities:**")
                    for activity in resume.co_curricular_activities:
                        st.write(f"- {activity}")
            else:
                st.info("Upload/Paste and parse a resume to see extracted information")
    
    # Tab 2: Job Matching
    with tab2:
        st.header("Job Matching Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Job Description")
            job_input_type = st.radio("Job Input Method:", ["Upload File", "Paste Text"], key="job_input")
            
            job = None
            if job_input_type == "Upload File":
                uploaded_job_file = st.file_uploader(
                    "Upload Job Description (PDF, DOCX, TXT, or Image)",
                    type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'],
                    key="job_file"
                )

                if uploaded_job_file:
                    _ext = Path(uploaded_job_file.name).suffix.lower()
                    if _ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'}:
                        st.info("🖼️ Image file detected — OCR will extract text automatically.")

                if uploaded_job_file and st.button("Parse Job Description"):
                    with st.spinner("Parsing job description..."):
                        _jd_validation_err = None
                        try:
                            # Parse job file (image → OCR, otherwise native parser)
                            _JOB_IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}
                            parser = ResumeParser()  # Reuse parser for file reading
                            temp_path = Path("temp") / uploaded_job_file.name
                            temp_path.parent.mkdir(exist_ok=True)
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_job_file.getbuffer())

                            if temp_path.suffix.lower() in _JOB_IMAGE_EXTS:
                                from src.extraction.ocr_processor import OCRProcessor
                                ocr = OCRProcessor()
                                job_text = ocr.extract_text(temp_path)
                            else:
                                job_text = parser.parse_file(temp_path)
                            temp_path.unlink()  # Delete temp file

                            if _detect_document_type(job_text) == 'resume':
                                _jd_validation_err = "This file looks like a Resume, not a Job Description. Please upload a JD file here."
                            else:
                                job, error = parse_job_description(job_text)
                                if error:
                                    st.error(f"Error: {error}")
                                else:
                                    st.session_state.job = job
                                    st.session_state.job_parsed = True
                                    st.success("✅ Job description parsed!")
                        except Exception as e:
                            st.error(f"Error parsing file: {str(e)}")
                    if _jd_validation_err:
                        st.error(_jd_validation_err)
            else:
                job_text = st.text_area("Enter Job Description:", height=300, key="job_text")
                
                if job_text and st.button("Parse Job Description"):
                    if _detect_document_type(job_text) == 'resume':
                        st.error("This text looks like a Resume, not a Job Description. Please paste JD content here.")
                        st.stop()
                    job, error = parse_job_description(job_text)
                    
                    if error:
                        st.error(f"Error: {error}")
                    else:
                        st.session_state.job = job
                        st.session_state.job_parsed = True
                        st.success("✅ Job description parsed!")
        
        with col2:
            st.subheader("Match Results")
            
            if st.session_state.resume_parsed and st.session_state.job_parsed:
                if st.button("Calculate Match Score"):
                    with st.spinner("Analyzing match..."):
                        resume = st.session_state.resume
                        job = st.session_state.job

                        matcher = JobMatcher(
                            skill_weight=st.session_state.weight_skills / 100,
                            experience_weight=st.session_state.weight_experience / 100,
                            education_weight=st.session_state.weight_education / 100,
                        )
                        match_result = matcher.match_resume_to_job(resume, job)
                        
                        st.session_state.match_result = match_result

                        # Display results via shared helper (includes explainability + fairness note)
                        _display_match_result(match_result)
            else:
                st.info("Please parse both a resume and job description to perform matching")
    
    # Tab 3: Gap Analysis
    with tab3:
        st.header("Skill Gap Analysis")
        
        if st.session_state.resume_parsed and st.session_state.job_parsed:
            if st.button("Generate Gap Analysis"):
                with st.spinner("Analyzing gaps..."):
                    resume = st.session_state.resume
                    job = st.session_state.job
                    
                    analyzer = GapAnalyzer()
                    gap_analysis = analyzer.analyze_gaps(resume, job)
                    
                    st.session_state.gap_analysis = gap_analysis
                    
                    # Display skill gaps
                    st.subheader("Skill Coverage")
                    skill_gaps = gap_analysis['skill_gaps']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Required Skills Coverage", 
                                f"{skill_gaps['required_skills_coverage']}%")
                    with col2:
                        st.metric("Preferred Skills Coverage", 
                                f"{skill_gaps['preferred_skills_coverage']}%")
                    
                    # Experience gaps
                    st.subheader("Experience Analysis")
                    exp_gaps = gap_analysis['experience_gaps']
                    domain = exp_gaps.get('job_domain', 'this role')
                    st.write(f"**Relevant Experience in {domain}:**")
                    st.write(f"- Required: {exp_gaps['required_experience']} years")

                    relevant = exp_gaps['relevant_experience']
                    total = exp_gaps['total_experience']
                    if relevant > 0 and relevant != total:
                        st.write(f"- Candidate: {relevant} years  *(overall: {total} years)*")
                    else:
                        st.write(f"- Candidate: {total} years")

                    # Check overqualification from match result
                    _hfr = st.session_state.get('match_result', {}).get('hard_filter_results', {})
                    _overqualified = not _hfr.get('overqualification', {}).get('passed', True)
                    if _overqualified:
                        st.warning(f"⚠️ Overqualified: {_hfr['overqualification']['detail']}")
                    elif exp_gaps['meets_requirement']:
                        st.success("✅ Meets experience requirement")
                    else:
                        st.warning(f"⚠️ Gap: {exp_gaps['experience_gap_years']} years")
                    
                    # Improvement suggestions
                    st.subheader("Improvement Recommendations")
                    suggestions = gap_analysis['improvement_suggestions']
                    for i, suggestion in enumerate(suggestions, 1):
                        st.write(f"{i}. {suggestion}")
                    
                    # Priority areas
                    st.subheader("Priority Areas")
                    _area_meta = {
                        "Critical Skill Gaps": {
                            "icon": "🔴",
                            "description": (
                                "More than 3 required skills are missing. "
                                "Acquiring these is essential before applying."
                            ),
                        },
                        "Experience Requirement": {
                            "icon": "🟠",
                            "description": (
                                "Relevant experience falls short of the job requirement by "
                                f"more than 1 year "
                                f"(gap: {gap_analysis['experience_gaps'].get('experience_gap_years', 0):.1f} yr(s))."
                            ),
                        },
                        "Skill Development": {
                            "icon": "🟡",
                            "description": (
                                "Required-skills coverage is below 70 % "
                                f"(current: {gap_analysis['skill_gaps'].get('required_skills_coverage', 0):.0f} %). "
                                "Upskilling in the missing areas will improve the match significantly."
                            ),
                        },
                        "Minor Improvements": {
                            "icon": "🟢",
                            "description": (
                                "No critical gaps found. The candidate is a strong match. "
                                "Small refinements (preferred skills, certifications, resume wording) "
                                "can further strengthen the application."
                            ),
                        },
                    }
                    for area in gap_analysis['priority_areas']:
                        meta = _area_meta.get(area, {"icon": "⚪", "description": area})
                        st.markdown(
                            f"{meta['icon']} **{area}** — {meta['description']}"
                        )
                    
            # Download report button (outside the if block so it shows after analysis is done)
            if st.session_state.get('gap_analysis'):
                st.markdown("---")
                if st.button("📥 Generate Full Report (PDF)", type="primary"):
                    try:
                        with st.spinner("Generating PDF report..."):
                            resume = st.session_state.resume
                            job = st.session_state.job
                            match_result = st.session_state.get('match_result', {})
                            gap_analysis = st.session_state.gap_analysis
                            
                            report_gen = ReportGenerator()
                            pdf_buffer = report_gen.generate_pdf_report(
                                resume, job, match_result, gap_analysis
                            )
                            
                            st.download_button(
                                label="💾 Download PDF Report",
                                data=pdf_buffer,
                                file_name=f"screening_report_{resume.name or 'candidate'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                            st.success("✅ PDF report generated successfully!")
                    except ImportError as e:
                        st.error("⚠️ PDF generation requires reportlab. Install it with: pip install reportlab")
                        st.info("Alternatively, you can download a text report:")
                        # Fallback to text report
                        report_gen = ReportGenerator()
                        match_result = st.session_state.get('match_result', {})
                        text_report = report_gen.generate_screening_report(
                            resume, job, match_result, gap_analysis
                        )
                        st.download_button(
                            label="Download Text Report",
                            data=text_report,
                            file_name="screening_report.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
                
                # Email sending section
                st.markdown("---")

                resume = st.session_state.resume
                job = st.session_state.job
                gap_analysis = st.session_state.gap_analysis
                match_result = st.session_state.get('match_result', {})

                # ── Decision ─────────────────────────────────────────────────
                overall_score = match_result.get('overall_score', 0)
                decision = match_result.get('decision', 'Reject')
                hard_filter_results = match_result.get('hard_filter_results', {})
                confidence_factor = match_result.get('confidence_factor', 1.0)

                # Hard filter summary
                if hard_filter_results:
                    st.subheader("� Eligibility Check")
                    for fv in hard_filter_results.values():
                        icon = "✅" if fv['passed'] else "❌"
                        st.write(f"{icon} **{fv['label']}**: {fv['detail']}")
                    if confidence_factor < 1.0:
                        st.caption(
                            f"ℹ️ Confidence factor applied: {confidence_factor} "
                            f"(sparse resume data reduced the raw score)"
                        )

                if decision == "Accept":
                    st.subheader("🎉 Decision")
                    st.success(
                        f"✅ **ACCEPT** — Score {overall_score}% ≥ 75%.  "
                        f"Candidate is recommended for interview."
                    )
                elif decision == "Review":
                    st.subheader("🔍 Decision")
                    st.warning(
                        f"🔍 **REVIEW** — Score {overall_score}% is in the review range (60–75%).  "
                        f"Manual review by hiring manager is recommended."
                    )
                else:
                    reason = match_result.get('decision_reason', '')
                    st.subheader("📋 Decision")
                    st.error(
                        f"❌ **REJECT** — {reason or f'Score {overall_score}% is below 60%.'}"
                    )

                # ── Email section ──────────────────────────────────────────────
                if decision in ("Accept", "Reject"):
                    # Accept → shortlist email to candidate
                    # Reject → rejection + gap report email to candidate
                    email_label = (
                        "📧 Send Interview Invitation"
                        if decision == "Accept" else
                        "📧 Send Rejection Email with Gap Report"
                    )
                    btn_label = (
                        "📤 Send Shortlist Email"
                        if decision == "Accept" else
                        "📤 Send Rejection Email"
                    )
                    st.subheader(email_label)
                    default_email = resume.email or ""
                    col_email, col_btn = st.columns([3, 1])
                    with col_email:
                        recipient_email = st.text_input(
                            "Recipient Email (To):",
                            value=default_email,
                            placeholder="candidate@example.com",
                            key="notify_to",
                            help="One or more addresses separated by commas"
                        )
                        cc_email_input = st.text_input(
                            "CC (optional):",
                            value="",
                            placeholder="hr@example.com",
                            key="notify_cc",
                            help="One or more CC addresses separated by commas"
                        )
                    with col_btn:
                        st.write("")
                        st.write("")
                        send_email_btn = st.button(btn_label, type="secondary")

                    if send_email_btn:
                        if not recipient_email.strip():
                            st.error("Please enter at least one recipient email address.")
                        elif not st.session_state.sender_email or not st.session_state.sender_password:
                            st.error("⚠️ Please configure email settings in the sidebar first.")
                        else:
                            to_list = [e.strip() for e in recipient_email.split(',') if e.strip()]
                            cc_list = [e.strip() for e in cc_email_input.split(',') if e.strip()]
                            with st.spinner(f"Sending email to {', '.join(to_list)}..."):
                                try:
                                    email_sender = EmailSender(
                                        smtp_port=st.session_state.smtp_port,
                                        use_ssl=st.session_state.use_ssl,
                                        timeout=30
                                    )
                                    creds = dict(
                                        sender_email=st.session_state.sender_email,
                                        sender_password=st.session_state.sender_password,
                                        cc_email=cc_list or None
                                    )
                                    if decision == "Accept":
                                        result = email_sender.send_shortlist_email(
                                            to_email=to_list,
                                            candidate_name=resume.name or "Candidate",
                                            company_name=job.company or "Our Company",
                                            job_title=job.title or "the applied position",
                                            **creds
                                        )
                                    else:
                                        report_gen = ReportGenerator()
                                        gap_report_text = report_gen.generate_gap_report(gap_analysis, match_result)
                                        result = email_sender.send_rejection_email(
                                            to_email=to_list,
                                            candidate_name=resume.name or "Candidate",
                                            company_name=job.company or "Our Company",
                                            job_title=job.title or "the applied position",
                                            gap_report=gap_report_text,
                                            **creds
                                        )
                                    if result['success']:
                                        st.success(f"✅ {result['message']}")
                                    else:
                                        st.error(f"❌ {result['message']}")
                                except Exception as e:
                                    st.error(f"Error sending email: {str(e)}")

                else:  # Review → forward to hiring manager with resume attached
                    st.subheader("📧 Send for Manual Review")
                    st.info(
                        "Forward the candidate's resume to the hiring manager for review. "
                        "A score of 60–75% requires human judgement."
                    )
                    col_email, col_btn = st.columns([3, 1])
                    with col_email:
                        review_to = st.text_input(
                            "Hiring Manager Email (To):",
                            placeholder="manager@company.com",
                            key="review_to",
                            help="Hiring manager's email address"
                        )
                        review_cc = st.text_input(
                            "CC (optional):",
                            value="",
                            placeholder="hr@company.com, recruiter@company.com",
                            key="review_cc",
                            help="One or more CC addresses separated by commas"
                        )
                    with col_btn:
                        st.write("")
                        st.write("")
                        send_review_btn = st.button("📤 Send Review Request", type="secondary")

                    resume_bytes = st.session_state.get('resume_file_bytes')
                    resume_fname = st.session_state.get('resume_file_name')
                    if resume_bytes:
                        st.caption(f"📎 Resume file '{resume_fname}' will be attached.")
                    else:
                        st.caption(
                            "ℹ️ No resume file available to attach "
                            "(resume was entered as text). "
                            "The email will be sent without an attachment."
                        )

                    if send_review_btn:
                        if not review_to.strip():
                            st.error("Please enter the hiring manager's email address.")
                        elif not st.session_state.sender_email or not st.session_state.sender_password:
                            st.error("⚠️ Please configure email settings in the sidebar first.")
                        else:
                            to_list = [e.strip() for e in review_to.split(',') if e.strip()]
                            cc_list = [e.strip() for e in review_cc.split(',') if e.strip()]
                            match_summary = (
                                f"Skills: {match_result.get('skill_score', 0)}% | "
                                f"Experience: {match_result.get('experience_score', 0)}% | "
                                f"Education: {match_result.get('education_score', 0)}%"
                            )
                            with st.spinner(f"Sending review request to {', '.join(to_list)}..."):
                                try:
                                    email_sender = EmailSender(
                                        smtp_port=st.session_state.smtp_port,
                                        use_ssl=st.session_state.use_ssl,
                                        timeout=30
                                    )
                                    result = email_sender.send_review_email(
                                        to_email=to_list,
                                        candidate_name=resume.name or "Candidate",
                                        company_name=job.company or "Our Company",
                                        job_title=job.title or "the applied position",
                                        overall_score=overall_score,
                                        sender_email=st.session_state.sender_email,
                                        sender_password=st.session_state.sender_password,
                                        cc_email=cc_list or None,
                                        resume_bytes=resume_bytes,
                                        resume_filename=resume_fname,
                                        match_summary=match_summary
                                    )
                                    if result['success']:
                                        st.success(f"✅ {result['message']}")
                                    else:
                                        st.error(f"❌ {result['message']}")
                                except Exception as e:
                                    st.error(f"Error sending email: {str(e)}")
        else:
            st.info("Please complete resume and job matching analysis first")

    # Tab 4: Analytics (Single Mode)
    with tab4:
        st.header("📈 Resume Analytics & Quality Score")

        if not st.session_state.resume_parsed:
            st.info("Please parse a resume in the Resume Analysis tab to view analytics.")
        else:
            resume = st.session_state.resume
            match_result = st.session_state.get('match_result', {})

            # Initialize analytics and quality scorer
            analytics = ScreeningAnalytics()
            quality_scorer = ResumeQualityScorer()

            # Get original resume text for quality analysis
            resume_text = ""  # We don't have the original text in session, so quality score will be limited

            # Two column layout
            col_left, col_right = st.columns(2)

            with col_left:
                # Resume Quality Score
                st.subheader("📝 Resume Quality Score")
                quality_result = quality_scorer.score_resume(resume, resume_text)

                # Display overall score
                score = quality_result['overall_score']
                grade = quality_result['grade']

                # Color-coded metric
                if score >= 80:
                    st.success(f"### {score}/100 — {grade}")
                elif score >= 60:
                    st.warning(f"### {score}/100 — {grade}")
                else:
                    st.error(f"### {score}/100 — {grade}")

                # Component breakdown
                st.write("**Component Scores:**")
                components = quality_result['component_scores']
                for component, value in components.items():
                    label = component.replace('_', ' ').title()
                    st.write(f"- {label}: {value:.1f}/25")

                # Strengths
                st.write("**✅ Strengths:**")
                for strength in quality_result['strengths']:
                    st.write(f"• {strength}")

                # Suggestions
                if quality_result['suggestions']:
                    st.write("**💡 Improvement Suggestions:**")
                    for idx, suggestion in enumerate(quality_result['suggestions'][:5], 1):
                        st.write(f"{idx}. {suggestion}")

            with col_right:
                # Profile Analytics
                st.subheader("👤 Profile Analytics")
                single_analytics = analytics.analyze_single_resume(resume, match_result)

                # Profile summary
                st.info(single_analytics['profile_summary'])

                # Key metrics
                met_col1, met_col2, met_col3 = st.columns(3)
                with met_col1:
                    st.metric("Total Skills", single_analytics['total_skills'])
                with met_col2:
                    st.metric("Experience", f"{single_analytics['experience_years']} yrs")
                with met_col3:
                    st.metric("Contact %", f"{single_analytics['contact_completeness']}%")

                # Experience level
                st.write(f"**Experience Level:** {single_analytics['experience_level']}")
                st.write(f"**Education:** {single_analytics['education_count']} degree(s)")
                st.write(f"**Certifications:** {single_analytics['certification_count']}")

                # Skills breakdown by category
                st.subheader("🔧 Skills by Category")
                skill_breakdown = single_analytics['skill_breakdown']

                if skill_breakdown:
                    import plotly.graph_objects as go
                    _is_light_s = st.session_state.get('theme', 'Dark') == 'Light'
                    _sfont = '#111111' if _is_light_s else '#f0f2f6'
                    _saxis = dict(
                        tickfont=dict(color=_sfont),
                        title=dict(font=dict(color=_sfont))
                    )

                    categories = list(skill_breakdown.keys())
                    counts = [len(skills) for skills in skill_breakdown.values()]

                    fig = go.Figure(data=[go.Bar(
                        x=categories,
                        y=counts,
                        marker_color='#4a6cf7',
                        text=counts,
                        textposition='auto',
                        textfont=dict(color=_sfont)
                    )])
                    fig.update_layout(
                        template='plotly' if _is_light_s else 'plotly_dark',
                        xaxis_title="Category",
                        yaxis_title="Number of Skills",
                        height=300,
                        margin=dict(l=20, r=20, t=30, b=20),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        font=dict(color=_sfont),
                        xaxis=_saxis,
                        yaxis=_saxis
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show skills in each category
                    with st.expander("View Skills by Category"):
                        for category, skills in skill_breakdown.items():
                            st.write(f"**{category}:**")
                            st.write(", ".join(skills))
                            st.write("")

            # If match analysis is done, show matching insights
            if st.session_state.get('match_result'):
                st.markdown("---")
                st.subheader("🎯 Match Analysis Insights")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Match", f"{match_result.get('overall_score', 0)}%")
                with col2:
                    st.metric("Skill Match", f"{match_result.get('skill_score', 0)}%")
                with col3:
                    st.metric("Experience Match", f"{match_result.get('experience_score', 0)}%")

                # Profile strengths and weaknesses
                col_str, col_weak = st.columns(2)
                with col_str:
                    st.write("**💪 Profile Strengths:**")
                    for strength in single_analytics['strengths']:
                        st.write(f"✅ {strength}")

                with col_weak:
                    if single_analytics['weaknesses']:
                        st.write("**🔍 Areas for Improvement:**")
                        for weakness in single_analytics['weaknesses']:
                            st.write(f"⚠️ {weakness}")

    _render_sidebar()


if __name__ == "__main__":
    main()
