"""
AI-Powered Resume Screening System
Streamlit Web Application
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

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


def parse_resume(file_or_text, is_file=True):
    """Parse resume and extract information"""
    try:
        parser = ResumeParser()
        
        # Parse resume text
        IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}

        if is_file:
            # Save uploaded file temporarily
            temp_path = Path("temp") / file_or_text.name
            temp_path.parent.mkdir(exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(file_or_text.getbuffer())

            if temp_path.suffix.lower() in IMAGE_EXTS:
                # Image/scanned resume — route through OCR
                from src.extraction.ocr_processor import OCRProcessor, TESSERACT_AVAILABLE
                if not TESSERACT_AVAILABLE:
                    temp_path.unlink()
                    return None, (
                        "OCR dependencies not installed. "
                        "Run: pip install pytesseract Pillow opencv-python"
                    )
                ocr = OCRProcessor()
                resume_text = ocr.extract_text(temp_path)
            else:
                resume_text = parser.parse_file(temp_path)

            temp_path.unlink()  # Delete temp file
        else:
            resume_text = file_or_text
        
        # Extract entities
        entity_extractor = EntityExtractor()
        entities = entity_extractor.extract_all_entities(resume_text)
        
        # Extract skills
        skill_extractor = SkillExtractor()
        skills = skill_extractor.extract_skills(resume_text)
        
        # Extract experience
        experience_extractor = ExperienceExtractor()
        preprocessor = TextPreprocessor()
        sections = preprocessor.extract_sections(resume_text)
        
        experiences = experience_extractor.extract_experience(
            resume_text, 
            sections.get('experience', '')
        )
        
        total_exp = experience_extractor.calculate_total_experience(experiences)
        
        # If no experience extracted, try to get from summary
        if total_exp == 0:
            summary_exp = experience_extractor.extract_experience_summary(resume_text)
            if summary_exp:
                total_exp = summary_exp
        
        # Build education list
        education_list = []
        for edu in entities.get('education', []):
            education_list.append(Education(
                degree=edu.get('degree', ''),
                institution=edu.get('institution', 'N/A'),
                year=edu.get('year'),
                grade=None
            ))
        
        # Create Resume object
        resume = Resume(
            raw_text=resume_text,
            name=entities.get('name'),
            email=entities.get('email'),
            phone=entities.get('phone'),
            skills=skills,
            education=education_list,
            experience=experiences,
            certifications=entities.get('certifications', []),
            total_experience_years=total_exp
        )
        
        return resume, None
    
    except Exception as e:
        return None, str(e)


def parse_job_description(text):
    """Parse job description"""
    try:
        parser = JobDescriptionParser()
        parsed = parser.parse_text(text)
        
        # Extract skills from requirements
        skill_extractor = SkillExtractor()
        all_skills = skill_extractor.extract_skills(text)
        
        # Split into required and preferred (simplified logic)
        required_skills = all_skills[:len(all_skills)//2] if len(all_skills) > 4 else all_skills
        preferred_skills = all_skills[len(all_skills)//2:] if len(all_skills) > 4 else []
        
        # Extract experience requirement
        required_exp = parsed.get('experience', 0) or 0
        if required_exp == 0:
            # Try to extract from text
            import re
            match = re.search(r'(\d+)\+?\s*years?', text, re.IGNORECASE)
            if match:
                required_exp = float(match.group(1))
        
        # Extract title and company
        lines = text.strip().split('\n')
        title = lines[0].strip() if lines else "Software Engineer"
        company = "Company Name"
        
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

                if uploaded_file:
                    _ext = Path(uploaded_file.name).suffix.lower()
                    if _ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'}:
                        st.info("🖼️ Image file detected — OCR will extract text automatically.")
                
                if uploaded_file and st.button("Parse Resume"):
                    with st.spinner("Parsing resume..."):
                        resume, error = parse_resume(uploaded_file, is_file=True)
                        
                        if error:
                            st.error(f"Error: {error}")
                        else:
                            st.session_state.resume = resume
                            st.session_state.resume_parsed = True
                            st.success("✅ Resume parsed successfully!")
            else:
                resume_text = st.text_area("Paste Resume Text:", height=300)
                
                if resume_text and st.button("Parse Resume"):
                    with st.spinner("Parsing resume..."):
                        resume, error = parse_resume(resume_text, is_file=False)
                        
                        if error:
                            st.error(f"Error: {error}")
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
                st.write(f"- Total Experience: {resume.total_experience_years} years")
                
                st.write("**Skills:**")
                if resume.skills:
                    st.write(", ".join(resume.skills[:20]))
                else:
                    st.write("No skills detected")
                
                st.write("**Education:**")
                if resume.education:
                    for edu in resume.education:
                        st.write(f"- {edu.degree} from {edu.institution}")
                else:
                    st.write("No education information found")
                
                st.write("**Experience:**")
                if resume.experience:
                    for exp in resume.experience[:3]:
                        st.write(f"- {exp.title} at {exp.company}")
                else:
                    st.write("No work experience found")
            else:
                st.info("Upload and parse a resume to see extracted information")
    
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
                            
                            job, error = parse_job_description(job_text)
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.session_state.job = job
                                st.session_state.job_parsed = True
                                st.success("✅ Job description parsed!")
                        except Exception as e:
                            st.error(f"Error parsing file: {str(e)}")
            else:
                job_text = st.text_area("Enter Job Description:", height=300, key="job_text")
                
                if job_text and st.button("Parse Job Description"):
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
                    st.write(f"Required: {exp_gaps['required_experience']} years")
                    st.write(f"Candidate: {exp_gaps['candidate_experience']} years")
                    
                    if exp_gaps['meets_requirement']:
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
                    for area in gap_analysis['priority_areas']:
                        st.write(f"- {area}")
                    
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
                st.subheader("📧 Email Gap Analysis Report")
                
                resume = st.session_state.resume
                gap_analysis = st.session_state.gap_analysis
                
                # Get email from resume or allow manual input
                default_email = resume.email or ""

                col_email, col_btn = st.columns([3, 1])
                with col_email:
                    recipient_email = st.text_input(
                        "Send Gap Analysis to (To):",
                        value=default_email,
                        placeholder="candidate@example.com, manager@example.com",
                        help="One or more recipient email addresses separated by commas"
                    )
                    cc_email = st.text_input(
                        "CC (optional):",
                        value="",
                        placeholder="hr@example.com, reviewer@example.com",
                        help="One or more CC email addresses separated by commas (optional)"
                    )
                
                with col_btn:
                    st.write("")  # Spacer for alignment
                    st.write("")  # Spacer for alignment
                    send_email_btn = st.button("📤 Send Email", type="secondary")
                
                if send_email_btn:
                    if not recipient_email:
                        st.error("Please enter at least one recipient email address")
                    elif not st.session_state.sender_email or not st.session_state.sender_password:
                        st.error("⚠️ Please configure email settings in the sidebar first")
                    else:
                        to_list = [e.strip() for e in recipient_email.split(',') if e.strip()]
                        cc_list = [e.strip() for e in cc_email.split(',') if e.strip()] if cc_email else []
                        display_to = ', '.join(to_list)
                        with st.spinner(f"Sending email to {display_to}..."):
                            try:
                                # Generate the gap analysis report text
                                report_gen = ReportGenerator()
                                report_content = report_gen.generate_gap_report(gap_analysis)
                                
                                # Send email with configured settings
                                email_sender = EmailSender(
                                    smtp_port=st.session_state.smtp_port,
                                    use_ssl=st.session_state.use_ssl,
                                    timeout=30
                                )
                                result = email_sender.send_gap_analysis_report(
                                    to_email=to_list,
                                    candidate_name=resume.name or "Candidate",
                                    report_content=report_content,
                                    sender_email=st.session_state.sender_email,
                                    sender_password=st.session_state.sender_password,
                                    cc_email=cc_list if cc_list else None
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
