# Quick Start Guide

## AI-Powered Resume Screening System

This guide will help you get started with the application in under 5 minutes.

---

## Installation (2 minutes)

### Step 1: Open PowerShell/Terminal

Navigate to project directory:
```powershell
cd "c:\Users\sobasu\Downloads\BITS Pilani\4th Sem\dissertation"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

**Note:** spaCy is optional but recommended for advanced NLP:
```powershell
python -m spacy download en_core_web_sm
```

✅ **Installation Complete!**

---

## Running the Application (1 minute)

### Option A: Web UI (Recommended)

```powershell
streamlit run ui/app.py
```

Browser opens automatically at `http://localhost:8501`

### Option B: Quick CLI Demo

```powershell
python main.py
```

Select option `2` for CLI demo.

---

## Testing the Application (3 minutes)

### Quick Workflow Test

1. **Start Web Application**
   ```powershell
   streamlit run ui/app.py
   ```

2. **Upload Sample Resume**
   - Click on "Resume Analysis" tab
   - Click "Upload File"
   - Navigate to: `data/sample_resumes/sample_resume_1.txt`
   - Click "Parse Resume"
   - ✅ View extracted information on the right

3. **Load Job Description**
   - Go to "Job Matching" tab
   - Open `data/sample_jobs/job_description_1.txt` in notepad
   - Copy entire content
   - Paste into text area
   - Click "Parse Job Description"
   - ✅ Job requirements extracted

4. **Calculate Match**
   - Click "Calculate Match Score"
   - ✅ View match percentage (should be 70-85%)
   - ✅ See matched and missing skills

5. **Generate Gap Analysis**
   - Go to "Gap Analysis" tab
   - Click "Generate Gap Analysis"
   - ✅ View skill coverage and recommendations

6. **Download Report**
   - Click "Download Full Report"
   - ✅ Text file saved with complete analysis

### Email Feature Test (Optional)

**Prerequisites:** Valid email account (Outlook/Gmail)

1. **Configure Email (Sidebar)**
   - Select "Outlook/Hotmail" (recommended for beginners)
   - Enter your Outlook email
   - Enter your Outlook password
   - Click "🔌 Test Connection"
   - ✅ Should show "Successfully connected"

2. **Send Report via Email**
   - In Gap Analysis tab, enter recipient email
   - Click "📤 Send Email"
   - ✅ Success message displayed
   - ✅ Email received within 1-2 minutes

**If using Gmail:** Requires App Password (see setup below)

---

## Email Setup for Gmail Users

### Gmail Requires App Password

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow setup instructions

2. **Generate App Password**
   - In Security settings, scroll to "App passwords"
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password

3. **Use in Application**
   - Select "Gmail" in email provider
   - Enter your Gmail address
   - Paste the App Password (not regular password)
   - Test connection

### Troubleshooting Email Connection

**Error: Connection timeout**

1. **First, try Outlook instead of Gmail:**
   - Select "Outlook/Hotmail" from dropdown
   - Use regular Microsoft password
   - Works better with firewalls

2. **If still failing:**
   - Try "Gmail (SSL)" option
   - Connect to mobile hotspot
   - Check Windows Firewall settings
   - See detailed troubleshooting in app sidebar

---

## Common Commands

### Run Web Application
```powershell
streamlit run ui/app.py
```

### Run on Different Port
```powershell
streamlit run ui/app.py --server.port 8502
```

### Run CLI Demo
```powershell
python main.py
```

### Run Tests
```powershell
pytest tests/ -v
```

### Deactivate Virtual Environment
```powershell
deactivate
```

### Stop Web Server
Press `Ctrl + C` in terminal

---

## Project Structure Overview

```
dissertation/
├── src/                    # Core source code
│   ├── data/              # Parsing modules
│   ├── extraction/        # Information extraction
│   ├── matching/          # Job matching logic
│   ├── analysis/          # Gap analysis
│   ├── models/            # Data models
│   └── utils/             # Utilities
├── ui/                    # Web interface
│   └── app.py            # Streamlit app
├── data/                  # Sample data
│   ├── sample_resumes/   # Test resumes
│   ├── sample_jobs/      # Test job descriptions
│   └── skills_database.json
├── tests/                 # Unit tests
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # Full documentation
```

---

## Key Features

✅ **Resume Parsing**
- PDF, DOCX, TXT support
- Automatic info extraction
- Direct text paste option

✅ **Skill Matching**
- 100+ skills database
- Smart matching algorithm
- Match score calculation

✅ **Gap Analysis**
- Identify missing skills
- Get improvement suggestions
- Priority-based recommendations

✅ **Reports**
- Detailed screening reports
- Downloadable text format
- Email delivery option

✅ **Email Integration**
- Multiple providers (Gmail, Outlook, Yahoo)
- Secure SMTP configuration
- Connection testing
- Professional email formatting

---

## Troubleshooting

**Problem:** Module not found
```powershell
pip install -r requirements.txt
```

**Problem:** spaCy model missing (optional)
```powershell
python -m spacy download en_core_web_sm
```

**Problem:** Port already in use
```powershell
streamlit run ui/app.py --server.port 8502
```

**Problem:** Email connection timeout
- Try Outlook/Hotmail instead of Gmail
- Switch to Gmail (SSL) option
- Connect to mobile hotspot
- See app sidebar for detailed troubleshooting

**Problem:** Gmail authentication failed
- Use App Password, not regular password
- Enable 2-Step Verification first
- Generate password at: https://myaccount.google.com/apppasswords

---

## Sample Workflow

1. Parse resume → Extract info
2. Load job description → Parse requirements
3. Calculate match → View scores
4. Generate gap analysis → Get recommendations
5. Download report OR Email to candidate
6. Configure email (one-time) → Test connection

---

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Explore [notebooks/exploration.ipynb](notebooks/exploration.ipynb)
- Try with your own resumes
- Customize skills database

---

## Support

- Check README.md for detailed guides
- Review test cases for examples
- See CONTRIBUTING.md for development

---

**Ready to start? Run:**
```powershell
streamlit run ui/app.py
```

**Happy screening! 🚀**
