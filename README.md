# AI-Powered Resume Screening System

## BITS Pilani Dissertation Project

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An intelligent system for automated resume screening and job matching using Natural Language Processing (NLP) and Machine Learning techniques. This project aims to support recruitment decision-making by automating resume analysis, skill extraction, candidate-job matching, and providing actionable feedback to applicants.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How to Use](#how-to-use)
- [Testing the Application](#testing-the-application)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Sample Data](#sample-data)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This dissertation project lies at the intersection of **Artificial Intelligence** and **Natural Language Processing**, focusing on the analysis of unstructured textual data such as resumes and job descriptions. The system automates the resume screening process and provides intelligent insights for both recruiters and job seekers.

### Key Objectives

1. **Resume Text Analysis**: Parse and analyze unstructured resume data using NLP techniques
2. **Information Extraction**: Extract skills, experience, qualifications, and personal information
3. **Intelligent Matching**: Match candidate profiles with job requirements using similarity algorithms
4. **Gap Analysis**: Identify skill gaps and provide improvement recommendations
5. **Automated Screening**: Generate comprehensive screening reports for recruiters

---

## ✨ Features

### Core Functionality

- **Multi-Format Resume Parsing**
  - Support for PDF, DOCX, and TXT formats
  - Automatic text extraction and preprocessing
  - Direct text paste option
  
- **Intelligent Information Extraction**
  - Personal details (name, email, phone)
  - Skills and technologies (100+ skills database)
  - Work experience with duration calculation
  - Education and certifications
  
- **Job Description Analysis**
  - Parse job requirements and responsibilities
  - Extract required and preferred skills
  - Identify experience requirements
  - Automatic role classification
  
- **Smart Matching Algorithm**
  - Multi-dimensional scoring (skills, experience, education)
  - Weighted matching based on importance (Skills: 50%, Experience: 30%, Education: 20%)
  - Match level classification (Poor/Fair/Good/Excellent)
  - Detailed skill-by-skill comparison
  
- **Comprehensive Gap Analysis**
  - Skill coverage assessment with percentages
  - Missing skills identification (required vs preferred)
  - Experience gap calculation
  - Personalized improvement suggestions
  - Priority-based recommendations
  
- **Report Generation**
  - Detailed screening reports
  - Gap analysis summaries
  - Downloadable text format
  - Professional formatting
  
- **📧 Email Integration**
  - Send gap analysis reports via email
  - Multiple email provider support (Gmail, Outlook, Yahoo, Custom)
  - Secure SMTP configuration (TLS/SSL)
  - Connection testing before sending
  - Support for Gmail App Passwords
  - Firewall troubleshooting guidance

### User Interface

- **Web Application (Streamlit)**
  - Clean, intuitive interface
  - Resume upload and direct text input
  - Real-time job matching
  - Interactive gap analysis visualization
  - Report download functionality
  - Email configuration panel
  - Built-in troubleshooting guides
  
- **Command Line Interface**
  - Quick demo functionality
  - Sample data testing
  - Batch processing capabilities

---

## 📁 Project Structure

```
dissertation/
├── src/                          # Source code
│   ├── data/                     # Data parsing and preprocessing
│   │   ├── parser.py            # Resume and job description parsers
│   │   └── preprocessor.py      # Text preprocessing utilities
│   ├── extraction/               # Information extraction modules
│   │   ├── skill_extractor.py   # Skill extraction logic
│   │   ├── experience_extractor.py  # Experience extraction
│   │   └── entity_extractor.py  # Entity recognition
│   ├── matching/                 # Job matching algorithms
│   │   ├── job_matcher.py       # Matching logic
│   │   └── similarity.py        # Similarity calculations
│   ├── analysis/                 # Analysis and reporting
│   │   ├── gap_analyzer.py      # Gap analysis
│   │   └── report_generator.py  # Report generation
│   ├── models/                   # Data models
│   │   ├── resume.py            # Resume model
│   │   └── job.py               # Job description model
│   └── utils/                    # Utilities
│       ├── config.py            # Configuration
│       └── helpers.py           # Helper functions
├── ui/                           # User interface
│   └── app.py                   # Streamlit web application
├── data/                         # Data directory
│   ├── sample_resumes/          # Sample resume files
│   ├── sample_jobs/             # Sample job descriptions
│   └── skills_database.json     # Skills reference database
├── tests/                        # Unit tests
│   ├── test_parser.py
│   ├── test_extractor.py
│   └── test_matcher.py
├── notebooks/                    # Jupyter notebooks
│   └── exploration.ipynb        # Data exploration
├── temp/                         # Temporary files
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── README.md                     # This file
├── QUICKSTART.md                # Quick start guide
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                       # MIT License
└── .gitignore                   # Git ignore rules
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### Step 1: Clone or Navigate to the Project

```bash
cd "c:\Users\sobasu\Downloads\BITS Pilani\4th Sem\dissertation"
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Language Model

The system uses spaCy for NLP tasks. Download the English language model:

```bash
python -m spacy download en_core_web_sm
```

### Step 5: Verify Installation

```bash
python -c "import spacy; import streamlit; print('Installation successful!')"
```

---

## ⚡ Quick Start

### Option 1: Run Web Application (Recommended)

```bash
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

### Option 2: Run CLI Demo

```bash
python main.py
```

Select option `2` for CLI Demo to see a quick demonstration.

### Option 3: Use as Python Module

```python
from src.data.parser import ResumeParser
from src.extraction.skill_extractor import SkillExtractor

# Parse resume
parser = ResumeParser()
resume_text = parser.parse_file("path/to/resume.pdf")

# Extract skills
extractor = SkillExtractor()
skills = extractor.extract_skills(resume_text)
print(f"Skills found: {skills}")
```

---

## 📖 How to Use

### Web Application Guide

#### 1. Resume Analysis Tab

**Step 1:** Choose input method
- Upload File (PDF, DOCX, TXT)
- Paste Text directly

**Step 2:** Click "Parse Resume"
- System extracts personal information
- Identifies skills and technologies
- Analyzes work experience
- Processes education details

**Step 3:** Review extracted information
- Personal details displayed on the right
- Skills listed with categorization
- Experience timeline shown
- Education summary provided

#### 2. Job Matching Tab

**Step 1:** Enter job description
- Paste complete job posting
- Include requirements and qualifications

**Step 2:** Click "Parse Job Description"
- System extracts job requirements
- Identifies required skills
- Calculates experience needs

**Step 3:** Click "Calculate Match Score"
- Overall match percentage displayed
- Component scores shown (Skills, Experience, Education)
- Match level classification provided
- Recommendation generated

**View Results:**
- Overall Match Score (0-100%)
- Match Level (Poor/Fair/Good/Excellent)
- Matched Skills (highlighted in green)
- Missing Skills (highlighted in red)
- Detailed recommendation

#### 3. Gap Analysis Tab

**Step 1:** Complete resume and job matching first

**Step 2:** Click "Generate Gap Analysis"
- Skill coverage percentages
- Experience gap analysis
- Missing skills breakdown
- Priority improvement areas

**Step 3:** Review recommendations
- Specific action items provided
- Learning resources suggested
- Timeline estimates given

**Step 4:** Download or Email Report

**Option A: Download Report**
- Click "Download Full Report"
- Comprehensive text report generated
- Save for future reference

**Option B: Email Report to Candidate**
- Configure email settings in sidebar (one-time setup)
- Enter recipient email address
- Click "📤 Send Email"
- Professional gap analysis report delivered

#### 4. Email Configuration (Sidebar)

**Initial Setup:**

1. **Select Email Provider**
   - Gmail (default)
   - Gmail (SSL) - alternative for firewall issues
   - Outlook/Hotmail - recommended if Gmail times out
   - Yahoo Mail
   - Custom SMTP server

2. **Enter Credentials**
   - Sender email address
   - Password or App Password
   - For Gmail: Use App Password (requires 2-Step Verification)
   - For Outlook: Use regular password

3. **Test Connection**
   - Click "🔌 Test Connection" button
   - Verify successful connection before sending emails
   - If timeout occurs, see troubleshooting section

4. **Save Configuration**
   - Click "💾 Save Config"
   - Settings persist during session

**Gmail App Password Setup:**

1. Enable 2-Step Verification in Google Account
2. Go to Security > 2-Step Verification > App passwords
3. Generate new app password for "Mail"
4. Use generated password (not your regular Gmail password)
5. Paste into application

**Email Troubleshooting:**

If connection times out:
- Try Outlook/Hotmail instead of Gmail
- Switch to Port 465 (SSL) option
- Connect to mobile hotspot to bypass ISP restrictions
- Check Windows Firewall settings
- Temporarily disable antivirus for testing
- See detailed troubleshooting in application sidebar

---

## 🧪 Testing the Application

### Test Case 1: Complete Workflow Test

**Objective:** Test entire resume screening process

**Steps:**

1. **Start the application**
   ```bash
   streamlit run ui/app.py
   ```

2. **Upload Sample Resume**
   - Navigate to "Resume Analysis" tab
   - Click "Upload File"
   - Select `data/sample_resumes/sample_resume_1.txt`
   - Click "Parse Resume"
   
   **Expected Result:** 
   - Name: "JANE SMITH"
   - Email and phone extracted
   - Skills: Python, Django, React, PostgreSQL, AWS, Docker, etc.
   - Experience: ~6 years
   - Education: B.Tech Computer Science

3. **Load Sample Job**
   - Navigate to "Job Matching" tab
   - Open `data/sample_jobs/job_description_1.txt` in a text editor
   - Copy the entire content
   - Paste into "Enter Job Description" field
   - Click "Parse Job Description"
   
   **Expected Result:**
   - Job title parsed
   - Required skills identified
   - Experience requirement: 5+ years

4. **Calculate Match**
   - Click "Calculate Match Score"
   
   **Expected Result:**
   - Overall Match Score: 70-85%
   - Match Level: "Good Match" or "Excellent Match"
   - Matched skills displayed
   - Few or no critical missing skills
   - Positive recommendation

5. **Generate Gap Analysis**
   - Navigate to "Gap Analysis" tab
   - Click "Generate Gap Analysis"
   
   **Expected Result:**
   - High skill coverage (>80%)
   - Experience requirement met
   - Few improvement suggestions
   - Minor improvements category

6. **Download or Email Report**
   
   **Option A: Download**
   - Click "Download Full Report"
   
   **Expected Result:**
   - Text file downloaded
   - Contains all analysis details
   - Professional formatting
   
   **Option B: Email Report**
   - Configure email in sidebar (if not already done)
   - Enter recipient email: test@example.com
   - Click "📤 Send Email"
   
   **Expected Result:**
   - Success message displayed
   - Email delivered with gap analysis report
   - Professional email formatting

### Test Case 2: Mismatched Profile Test

**Objective:** Test system with non-matching resume

**Steps:**

1. **Upload Different Resume**
   - Use `data/sample_resumes/sample_resume_2.txt` (Data Scientist profile)
   
2. **Use Same Job Description**
   - Use `data/sample_jobs/job_description_1.txt` (Full Stack Engineer)
   
3. **Calculate Match**
   
   **Expected Result:**
   - Lower match score (40-60%)
   - Match Level: "Fair Match" or "Poor Match"
   - Multiple missing required skills
   - Experience gap identified
   - Recommendation: "Below requirements"

4. **Review Gap Analysis**
   
   **Expected Result:**
   - Lower skill coverage
   - Multiple missing skills listed
   - Actionable improvement suggestions
   - Learning path recommendations

### Test Case 3: Text Input Test

**Objective:** Test by pasting resume text

**Steps:**

1. **Select "Paste Text" option**
   
2. **Paste Resume Text**
   ```
   John Doe
   john@example.com | 555-1234
   
   SKILLS
   Python, Java, SQL, Git, Linux
   
   EXPERIENCE
   Software Developer at ABC Corp (2021-Present)
   - Developed web applications
   - Worked with databases
   
   EDUCATION
   BS Computer Science, 2020
   ```

3. **Parse and Analyze**
   
   **Expected Result:**
   - Basic information extracted
   - Skills identified: Python, Java, SQL, Git, Linux
   - Experience calculated: ~3 years
   - Education: BS Computer Science

### Test Case 4: CLI Demo Test

**Objective:** Test command-line interface

**Steps:**

1. **Run Main Script**
   ```bash
   python main.py
   ```

2. **Select Option 2** (Run CLI Demo)

3. **Review Output**
   
   **Expected Result:**
   - Sample resume parsed successfully
   - Skills detected and listed
   - Job description parsed
   - Match score calculated and displayed
   - Gap analysis performed
   - Full report can be viewed

### Test Case 5: Unit Tests

**Objective:** Run automated test suite

**Steps:**

1. **Install pytest** (if not already installed)
   ```bash
   pip install pytest pytest-cov
   ```

2. **Run All Tests**
   ```bash
   pytest tests/ -v
   ```
   
   **Expected Result:**
   - All tests pass
   - No errors or failures
   
3. **Run Specific Test Files**
   ```bash
   pytest tests/test_parser.py -v
   pytest tests/test_extractor.py -v
   pytest tests/test_matcher.py -v
   ```

4. **Generate Coverage Report**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   ```
   
   **Expected Result:**
   - Coverage report generated
   - Open `htmlcov/index.html` to view

### Test Case 6: Email Functionality Test

**Objective:** Test email sending and configuration

**Prerequisites:**
- Valid email account (Gmail App Password or Outlook account)
- Internet connection

**Steps:**

1. **Configure Email Settings**
   - Navigate to sidebar "📧 Email Configuration"
   - Select email provider (try Outlook/Hotmail first)
   - Enter sender email
   - Enter password (App Password for Gmail)
   
2. **Test Connection**
   - Click "🔌 Test Connection"
   
   **Expected Result:**
   - ✅ Success message: "Successfully connected to smtp.server:port"
   - If timeout, follow troubleshooting steps in sidebar
   
3. **Save Configuration**
   - Click "💾 Save Config"
   
   **Expected Result:**
   - ✅ "Configuration saved!" message

4. **Complete Resume Analysis**
   - Upload sample resume
   - Match with job description
   - Generate gap analysis

5. **Send Email Report**
   - Enter recipient email (can be same as sender)
   - Click "📤 Send Email"
   
   **Expected Result:**
   - ✅ Success message: "Gap analysis report successfully sent to..."
   - Email received in recipient inbox within 1-2 minutes
   - Email contains formatted gap analysis report

6. **Test Alternative Providers**
   - If Gmail times out, try:
     - Outlook/Hotmail (usually bypasses firewall)
     - Gmail (SSL) port 465
     - Mobile hotspot connection
   
   **Expected Result:**
   - At least one provider should work
   - Clear error messages guide troubleshooting

### Test Case 7: Error Handling Test

**Objective:** Test system robustness

**Tests to Perform:**

1. **Invalid File Upload**
   - Try uploading non-resume file (e.g., image)
   - **Expected:** Error message displayed gracefully

2. **Empty Input**
   - Submit empty text field
   - **Expected:** Validation message shown

3. **Malformed Resume**
   - Submit resume with minimal information
   - **Expected:** System extracts what it can, no crash

4. **Very Long Text**
   - Paste extremely long text (10+ pages)
   - **Expected:** Processing completes, may take longer

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   User Input    │
│ (Resume/Job)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Parser    │
│  (PDF/DOCX/TXT) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessor   │
│ (NLP Pipeline)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Extractors    │
│ Skills/Exp/Edu  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Job Matcher    │
│ (Scoring Logic) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gap Analyzer   │
│  (Insights)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Report Generator│
│   (Output)      │
└─────────────────┘
```

### Key Components

1. **Data Layer**
   - Resume Parser: Extracts text from various formats
   - Preprocessor: Cleans and structures text data
   
2. **Extraction Layer**
   - Skill Extractor: Identifies technical and soft skills
   - Experience Extractor: Parses work history
   - Entity Extractor: Recognizes names, contacts, education
   
3. **Analysis Layer**
   - Job Matcher: Calculates compatibility scores
   - Similarity Calculator: Measures text/skill similarity
   - Gap Analyzer: Identifies improvement areas
   
4. **Presentation Layer**
   - Web UI: Interactive Streamlit interface
   - CLI: Command-line demonstration
   - Report Generator: Formatted output

---

## 🛠️ Technologies Used

### Core Technologies

- **Python 3.8+**: Primary programming language
- **spaCy**: Natural Language Processing
- **Streamlit**: Web application framework
- **PyPDF2**: PDF parsing
- **python-docx**: DOCX file handling

### Libraries & Frameworks

- **NumPy & Pandas**: Data manipulation
- **scikit-learn**: Machine learning utilities  
- **NLTK**: Natural language toolkit
- **Regular Expressions**: Pattern matching
- **smtplib**: Email sending (SMTP protocol)
- **socket**: Network connection handling

### Development Tools

- **pytest**: Unit testing
- **black**: Code formatting
- **flake8**: Code linting
- **Git**: Version control

---

## 📊 Sample Data

The project includes sample data for testing:

### Sample Resumes

1. **sample_resume_1.txt**: Full Stack Engineer (6 years exp)
   - Skills: Python, React, Django, AWS, Docker
   - Strong match for Software Engineer positions

2. **sample_resume_2.txt**: Data Scientist (4 years exp)
   - Skills: Python, ML, TensorFlow, Statistics
   - Best match for Data Science roles

### Sample Job Descriptions

1. **job_description_1.txt**: Senior Full Stack Engineer
   - Required: 5+ years, Python, JavaScript, React, Cloud
   - Good benchmark for full-stack positions

2. **job_description_2.txt**: Machine Learning Engineer
   - Required: 3+ years, ML, Python, TensorFlow
   - Ideal for AI/ML role matching

### Skills Database

- **skills_database.json**: 100+ technical skills
- Categorized by type (languages, frameworks, tools)
- Easily extendable with new skills

---

## 🐛 Troubleshooting

### Common Issues

**Issue 1: spaCy model not found**
```bash
OSError: [E050] Can't find model 'en_core_web_sm'
```
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

**Issue 2: Module import errors**
```bash
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:**
```bash
pip install -r requirements.txt
```

**Issue 3: PDF parsing fails**
```bash
Error: Unable to parse PDF
```
**Solution:**
- Ensure PDF is not password-protected
- Try converting to text format first
- Check file is not corrupted

**Issue 4: Port already in use**
```bash
Port 8501 is in use
```
**Solution:**
```bash
streamlit run ui/app.py --server.port 8502
```

**Issue 5: Email connection timeout (WinError 10060)**
```bash
Connection timeout to smtp.gmail.com:587
```
**Solution:**
1. **Try Outlook/Hotmail instead:**
   - Select "Outlook/Hotmail" from Email Provider dropdown
   - Use regular Microsoft password
   - Outlook often bypasses firewall restrictions

2. **Try Gmail with SSL (Port 465):**
   - Select "Gmail (SSL)" option
   - Test connection again

3. **Use Mobile Hotspot:**
   - Connect PC to phone's mobile hotspot
   - Test email connection
   - Mobile networks typically don't block SMTP

4. **Fix Windows Firewall (Run as Administrator):**
   ```powershell
   New-NetFirewallRule -DisplayName "Allow SMTP 587" -Direction Outbound -Protocol TCP -LocalPort 587 -Action Allow
   New-NetFirewallRule -DisplayName "Allow SMTP 465" -Direction Outbound -Protocol TCP -LocalPort 465 -Action Allow
   ```

5. **Temporarily disable antivirus** and test

**Issue 6: Gmail authentication failed**
```bash
Authentication failed
```
**Solution:**
- Gmail requires App Password, not regular password
- Enable 2-Step Verification first
- Generate App Password: https://myaccount.google.com/apppasswords
- Use generated password in application

---

## 📈 Future Enhancements

### Recently Implemented ✅

1. **Email Integration** (Completed)
   - Multi-provider SMTP support (Gmail, Outlook, Yahoo)
   - Secure TLS/SSL connections
   - Connection testing and troubleshooting
   - Professional report formatting in emails

### Planned Features

1. **Advanced ML Models**
   - Deep learning for resume parsing
   - Transformer-based skill extraction (BERT, GPT)
   - Automated job role classification
   - Resume quality scoring

2. **Enhanced Matching**
   - Semantic similarity using embeddings
   - Context-aware skill matching
   - Industry-specific weights and benchmarks
   - Candidate ranking system

3. **Additional Features**
   - Bulk resume processing (batch upload)
   - ATS (Applicant Tracking System) integration
   - Interview question suggestions based on role
   - Salary range predictions
   - Resume improvement suggestions (grammar, formatting)
   - Cover letter analysis
   - LinkedIn profile integration
 
4. **Email Enhancements**
   - HTML formatted emails with charts
   - Email templates customization
   - Scheduled email delivery
   - Email tracking and analytics
   - Attachment support (PDF reports)

5. **UI Improvements**
   - Dark mode
   - Mobile responsive design
   - Dashboard with analytics
   - Export to multiple formats (PDF, Excel)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**BITS Pilani Student**
- Dissertation Project - 4th Semester
- Course: AI and Natural Language Processing

---

## 🙏 Acknowledgments

- BITS Pilani faculty for guidance
- spaCy team for excellent NLP library
- Streamlit for intuitive web framework
- Open source community for inspiration

---

## 📞 Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing [Issues](https://github.com/yourusername/dissertation/issues)
3. Create a new issue with detailed description
4. Contact project maintainer

---

## 📚 References

1. Natural Language Processing with Python (NLTK documentation)
2. spaCy Industrial-Strength NLP
3. Resume Parsing Techniques (Various research papers)
4. Machine Learning for Text Analysis
5. Streamlit Documentation

---

**Last Updated**: February 2026

**Project Status**: ✅ Active Development

**Version**: 1.0.0

---

*This project is submitted as part of the dissertation requirements for BITS Pilani.*
# bits-dissertation
