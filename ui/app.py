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
        r'about\s+this\s+role',
        r"we(?:\s+are|'re)\s+(?:looking|seeking|hiring)",  # "we are looking" + "we're looking"
        r'you\s+will\s+be\s+responsible', r'key\s+responsibilities',
        r'responsibilities', r'requirements', r'qualifications',
        r"what\s+you'?ll\s+(?:do|work|build)", r"what\s+we'?re\s+looking\s+for",
        r'the\s+ideal\s+candidate', r'required\s+qualifications?',
        r'preferred\s+qualifications?',
        r'required\s+skills?', r'preferred\s+skills?',   # "REQUIRED SKILLS / PREFERRED SKILLS"
        r'minimum\s+\d',                                 # "Minimum 3 years..."
        r'minimum\s+(?:experience|qualifications?)',
        r'equal\s+opportunity\s+employer', r'salary\s+range', r'compensation',
        r'benefits\s+include', r'apply\s+now', r'apply\s+today',
        r'we\s+offer', r'what\s+you\s+bring', r'nice\s+to\s+have',
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

    if jd_score >= 2 and jd_score > resume_score:
        return 'jd'
    if resume_score >= 2 and resume_score >= jd_score:
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


def main():
    """Main application"""
    initialize_session_state()
    
    st.title("🤖 AI-Powered Resume Screening System")
    st.markdown("### Intelligent Resume Analysis and Job Matching")
    
    st.markdown("---")
    
    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📄 Resume Analysis", "🔍 Job Matching", "📊 Gap Analysis"])
    
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
                        
                        matcher = JobMatcher()
                        match_result = matcher.match_resume_to_job(resume, job)
                        
                        st.session_state.match_result = match_result
                        
                        # Display results
                        st.metric("Overall Match Score", f"{match_result['overall_score']}%")

                        _dec = match_result.get('decision', '')
                        _reason = match_result.get('decision_reason', '')
                        if _dec == "Accept":
                            st.success(f"✅ **Decision: ACCEPT** — {_reason}")
                        elif _dec == "Review":
                            st.warning(f"🔍 **Decision: REVIEW** — {_reason}")
                        else:
                            st.error(f"❌ **Decision: REJECT** — {_reason}")

                        hfr = match_result.get('hard_filter_results', {})
                        if hfr:
                            st.write("**Eligibility Check:**")
                            overqualified = not hfr.get('overqualification', {}).get('passed', True)
                            for key, fv in hfr.items():
                                if key == 'experience' and overqualified:
                                    # Suppress the "✅ Minimum Experience" pass when overqualification fails
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
                        
                        # Matched skills
                        if match_result.get('matched_skills'):
                            st.write("**Matched Skills:**")
                            st.success(", ".join(match_result['matched_skills'][:10]))
                        
                        # Missing skills
                        if match_result.get('missing_required_skills'):
                            st.write("**Missing Required Skills:**")
                            st.error(", ".join(match_result['missing_required_skills']))
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
                                        gap_report_text = report_gen.generate_gap_report(gap_analysis)
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

    # Sidebar with information
    with st.sidebar:
        st.header("About")
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
        
        st.header("How to Use")
        st.write("""
        1. **Resume Analysis**: Upload or paste a resume (PDF/DOCX/TXT or image)
        2. **Job Matching**: Upload or enter a job description (same formats)
        3. **Gap Analysis**: View detailed skill gaps and improvement suggestions
        
        *Image files (PNG, JPG, TIFF, BMP) are processed via OCR automatically.*
        """)
        
        st.markdown("---")
        st.header("📧 Email Configuration")
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
            2. Enable 2-Step Verification
            3. Go to Security > 2-Step Verification > App passwords
            4. Generate a new app password
            5. Use that password here (not your regular Gmail password)
            """)


if __name__ == "__main__":
    main()
