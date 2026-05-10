# Quick Start Guide

## AI-Powered Resume Screening System

This guide will help you get started with the application in under 5 minutes.

---

## Prerequisites

- Python 3.10+ installed
- (Optional) Tesseract OCR — required only for scanned image / PDF input
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki
  - Add install dir (e.g. `C:\Program Files\Tesseract-OCR`) to your `PATH`

---

## Installation (2 minutes)

### Step 1: Open PowerShell and navigate to the project

```powershell
cd "c:\Users\sobasu\Downloads\BITS Pilani\4th Sem\dissertation"
```

### Step 2: Create and activate a virtual environment

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

> **Optional:** Install spaCy model for advanced NLP (the system works without it via regex fallbacks):
> ```powershell
> python -m spacy download en_core_web_sm
> ```

✅ **Installation complete!**

---

## Running the Application (1 minute)

### Web UI (Recommended)

```powershell
streamlit run ui/app.py
```

Browser opens automatically at `http://localhost:8501`

To use a different port:

```powershell
streamlit run ui/app.py --server.port 8502
```

### CLI Demo

```powershell
python main.py
```

Select option `2` for a CLI walkthrough using the bundled sample data.

---

## Quick Workflow — Single Mode (3 minutes)

1. **Start the Web Application**
   ```powershell
   streamlit run ui/app.py
   ```

2. **Select Processing Mode**
   - In the **Resume Analysis** tab, confirm **Single** is selected (default).

3. **Upload a Resume**
   - Click **Upload File** → navigate to `data/sample_resumes/sample_resume_1.txt`
   - Click **Parse Resume**
   - ✅ Extracted name, email, skills, experience, and education appear on the right

4. **Load a Job Description**
   - Switch to the **Job Matching** tab
   - Click **Upload File** → navigate to `data/sample_jobs/job_description_1.txt`
   - Click **Parse Job Description**
   - ✅ Required skills, preferred skills, and experience requirement extracted

5. **Calculate Match Score**
   - Click **Calculate Match Score**
   - ✅ Overall score, decision (Accept / Review / Reject), matched skills, and missing skills displayed
   - Expand **"🔍 Why this score?"** to see the per-component contribution table

6. **Generate Gap Analysis**
   - Switch to the **Gap Analysis** tab
   - Click **Generate Gap Analysis**
   - ✅ Skill coverage percentages, experience gap, improvement suggestions, and learning path shown
   - Click **Download PDF Report** to save locally

7. **View Analytics**
   - Switch to the **Analytics** tab
   - ✅ Resume Quality Score (0–100) with grade and component breakdown
   - ✅ Skills-by-Category bar chart
   - ✅ Profile strengths and (if any) areas for improvement

---

## Quick Workflow — Batch Mode

1. In the **Resume Analysis** tab, select **Batch** as the Processing Mode.

2. **Upload up to 10 resumes** → Click **Parse All Resumes**
   - Progress bar tracks each file
   - Collapsible expanders show per-resume results

3. Switch to **Job Matching** tab → Upload one JD → Click **Parse Job Description**

4. Click **Calculate Match Scores**
   - 🏆 Ranking leaderboard shows all candidates sorted by score (🥇🥈🥉 for top 3)
   - Expand any candidate for full match details and "Why this score?" explainability

5. Switch to **Gap Analysis** tab → Click **Generate All Gap Analyses**
   - Each candidate has a collapsible section with PDF download and email option

6. Switch to **Analytics** tab
   - Score distribution, decision breakdown chart, experience distribution
   - Candidate Comparison Table — click **📥 Download Comparison Table (CSV)** to export

---

## Adjusting Matching Weights

Open the **sidebar** → expand **⚖️ Matching Weights**:

- Move the **Skills**, **Experience**, and **Education** sliders
- All three must sum to exactly **100 %** (a green ✅ confirms; warnings shown otherwise)
- Changing weights invalidates existing results — re-run match calculation to apply new weights

---

## Email Feature (Optional)

**Configure once per session (sidebar → 📧 Email Configuration):**

1. Enter your sender email and password / App Password
2. Select connection type: Port 587 (TLS) or Port 465 (SSL)
3. Click **🔌 Test Connection** — wait for ✅ confirmation
4. Click **💾 Save Config**

**Send a report:**

- In the Gap Analysis tab (single or batch), enter the recipient email and click **📤 Send Email**

**Gmail users:** Regular passwords are rejected — you must use an App Password:
1. Enable 2-Step Verification at https://myaccount.google.com/security
2. Security → App passwords → Generate → copy the 16-character password
3. Use that password in the application

**Tip:** Outlook/Hotmail works with your regular password and is less likely to be blocked by firewalls.

---

## Running Evaluation Metrics

```powershell
python evaluate.py
```

Prints Precision / Recall / F1 for all 7 extraction modules and matching metrics (Accuracy, MAE, Spearman's ρ).

```powershell
python evaluate.py --json         # machine-readable output
python evaluate.py --save         # writes temp/eval_results.json
```

---

## Running Tests

```powershell
pytest tests/ -v
```

Run a single module:

```powershell
pytest tests/test_matcher.py -v
pytest tests/test_analytics.py -v
```

---

## Common Commands Reference

| Task | Command |
|---|---|
| Start web app | `streamlit run ui/app.py` |
| Start on different port | `streamlit run ui/app.py --server.port 8502` |
| CLI demo | `python main.py` |
| Run evaluation | `python evaluate.py` |
| Run all tests | `pytest tests/ -v` |
| Run with coverage | `pytest tests/ --cov=src --cov-report=html` |
| Deactivate venv | `deactivate` |
| Stop web server | `Ctrl + C` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| spaCy model missing (optional) | `python -m spacy download en_core_web_sm` |
| Port already in use | `streamlit run ui/app.py --server.port 8502` |
| `TesseractNotFoundError` | Install Tesseract, add to PATH |
| Scripts disabled (activation fails) | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` |
| Email connection timeout | Try Port 465 (SSL) or mobile hotspot |
| Gmail auth failed | Use App Password, not regular password |
| Match results disappeared | Expected — re-run after changing weights |

---

## Project Structure (Summary)

```
dissertation/
├── src/                    # Core source code
│   ├── data/              # Parsing modules (PDF, DOCX, TXT)
│   ├── extraction/        # Information extraction (skills, experience, OCR)
│   ├── matching/          # Job matching logic (configurable weights)
│   ├── analysis/          # Gap analysis, analytics, quality scorer, reports
│   ├── evaluation/        # Precision/Recall/F1 evaluation framework
│   ├── models/            # Resume and JobDescription dataclasses
│   └── utils/             # Config, helpers, email sender
├── ui/
│   └── app.py            # Streamlit web application
├── data/
│   ├── sample_resumes/   # 20+ test resumes (TXT, PDF, DOCX, images)
│   ├── sample_jobs/      # 20+ test job descriptions
│   └── skills_database.json
├── tests/                 # pytest test suite
├── main.py               # CLI entry point
├── evaluate.py           # Standalone evaluation runner
└── requirements.txt
```

---

## Next Steps

- Read the full [README.md](README.md) for detailed feature documentation
- Explore [notebooks/exploration.ipynb](notebooks/exploration.ipynb) for data analysis examples
- Try with your own resumes and job descriptions
- Customise `data/skills_database.json` to add domain-specific skills
