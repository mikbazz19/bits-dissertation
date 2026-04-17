# AI-Powered Resume Screening System

## BITS Pilani Dissertation – CCZG628T

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An intelligent system for automated resume screening and job matching using Natural Language Processing (NLP) and rule-based machine learning techniques. The system supports recruiters by automating resume analysis and supports job seekers by providing actionable gap analysis and learning path recommendations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How to Use](#how-to-use)
- [Evaluation](#evaluation)
- [Testing](#testing)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Sample Data](#sample-data)
- [Troubleshooting](#troubleshooting)
- [Future Work](#future-work)

---

## 🎯 Overview

This dissertation project lies at the intersection of **Artificial Intelligence** and **Natural Language Processing**, focusing on the automated analysis of unstructured textual data such as resumes and job descriptions.

### Key Objectives

1. **Resume Text Analysis** – Parse and analyse unstructured resume data from multiple file formats
2. **Information Extraction** – Extract skills, experience, qualifications, and personal information
3. **Intelligent Matching** – Score candidate profiles against job requirements using a weighted algorithm
4. **Gap Analysis** – Identify skill and experience gaps with prioritised improvement suggestions
5. **Evaluation** – Quantitatively measure extraction and matching quality using Precision, Recall, F1-Score, and Spearman's ρ

---

## ✨ Features

### Multi-Format Resume Parsing

- PDF, Microsoft Word (DOCX), and plain text (TXT) via `ResumeParser`
- Scanned images (PNG, JPG, TIFF, BMP, WebP) and image-heavy PDFs via OCR (`OCRProcessor`)
- Direct text paste in the web UI
- Graceful UTF-8 / Latin-1 encoding fallback for text files

### Information Extraction

- **Personal entities** – name (first-line heuristic), email (RFC-5321 regex), phone (international formats)
- **Skills** – word-boundary regex matching against a curated JSON database of 100+ technologies across 8 categories
- **Work experience** – structured date-range parsing with total years calculation; fallback to summary-sentence extraction
- **Education** – 18 degree keywords (B.Tech, M.Tech, MBA, PhD, BSc, …), year, and institution
- **Certifications** – AWS Certified, PMP, CISSP, CompTIA, and section-list extraction

### Job Description Analysis

- Section segmentation (responsibilities, requirements, skills, education, experience) via keyword look-ahead
- Required and preferred skill extraction
- Years-of-experience parsing via `(\d+)\+?\s*years?\s*of\s*experience` patterns

### Matching Algorithm

- Weighted composite score: **Skills 50 %  ·  Experience 30 %  ·  Education 20 %**
- Match bands: Excellent (≥ 80 %), Good (60–80 %), Fair (40–60 %), Poor (< 40 %)
- `SimilarityCalculator` provides Jaccard, Cosine, SequenceMatcher, and Overlap (Szymkiewicz–Simpson) metrics
- `fuzzy_match()` catches near-synonyms (e.g., "ML" ↔ "Machine Learning") at a configurable threshold

### Gap Analysis

- Required and preferred skill coverage percentages
- Experience shortfall in years
- Education requirement check
- `_generate_suggestions()` maps gaps to top-5 missing skills, internship advice, and online programme recommendations
- `generate_learning_path()` pairs missing skills with resource type, platform, and estimated duration

### Report Generation

- **Screening Report** – full candidate vs. job summary
- **Gap Report** – skill coverage and priority action items
- **Comparison Report** – multi-candidate ranking table

### Web Application (Streamlit)

- Three-tab layout: Resume Analysis · Job Matching · Gap Analysis
- **Single / Batch processing mode** selectable from the Resume Analysis tab
  - **Single mode** – one resume against one JD (full workflow)
  - **Batch mode** – upload up to 10 resumes against one JD; results displayed in collapsible expanders
- File upload + text paste input
- Session state preserves parsed objects across tab switches
- Progress bars during batch parsing, matching, and gap analysis
- PDF report download and email dispatch per candidate
- Email dispatch to candidate via SMTP (TLS / SSL)
- Temporary uploaded files are written to `temp/` and deleted after parsing

### Email Integration

- `EmailSender` supports Gmail, Outlook/Hotmail, Yahoo, and custom SMTP servers
- TLS (port 587) and SSL (port 465) modes
- `test_connection()` validates credentials before dispatch
- Credential resolution from environment variables (`SENDER_EMAIL`, `SENDER_PASSWORD`) or runtime parameters

### Evaluation Package (`src/evaluation/`)

- `metrics.py` – `ModuleMetrics` dataclass with Precision, Recall, F1-Score computed properties; `ExtractionMetrics` (macro averages); `MatchingMetrics` (Shortlisting Accuracy, MAE, Spearman's ρ)
- `ground_truth.py` – hand-annotated labels for both sample resumes and jobs with recruiter decisions
- `evaluator.py` – `ExtractionEvaluator` runs 7 extraction modules against annotated data; corpus-level TP/FP/FN accumulation
- `matching_evaluator.py` – `MatchingEvaluator` compares system shortlisting against recruiter decisions
- `evaluate.py` – standalone CLI: `python evaluate.py [--json] [--save]`

---

## 📁 Project Structure

```
dissertation/
├── src/                            # Source packages
│   ├── data/                       # Parsing and preprocessing
│   │   ├── parser.py              # ResumeParser, JobDescriptionParser
│   │   └── preprocessor.py        # TextPreprocessor (optional spaCy / regex fallback)
│   ├── extraction/                 # Information extraction
│   │   ├── entity_extractor.py    # Name, email, phone, education, certifications
│   │   ├── skill_extractor.py     # Skill extraction + categorisation
│   │   ├── experience_extractor.py# Work history, date parsing, total years
│   │   ├── ocr_processor.py       # Tesseract OCR + OpenCV pre-processing
│   │   └── parser.py              # Extraction-layer helpers
│   ├── matching/                   # Matching engine
│   │   ├── job_matcher.py         # Weighted composite scorer
│   │   └── similarity.py          # Jaccard, Cosine, SequenceMatcher, Overlap
│   ├── analysis/                   # Analysis and reporting
│   │   ├── gap_analyzer.py        # Skill/experience/education gap analysis
│   │   └── report_generator.py    # Screening, gap, comparison reports
│   ├── evaluation/                 # Quantitative evaluation package
│   │   ├── metrics.py             # ModuleMetrics, ExtractionMetrics, MatchingMetrics
│   │   ├── ground_truth.py        # Annotated ground truth (resumes + jobs)
│   │   ├── evaluator.py           # ExtractionEvaluator (7 modules)
│   │   ├── matching_evaluator.py  # MatchingEvaluator (3 metrics)
│   │   └── __init__.py
│   ├── models/                     # Data models (dataclasses)
│   │   ├── resume.py              # Resume, Education, Experience
│   │   └── job.py                 # JobDescription
│   └── utils/                      # Utilities
│       ├── config.py              # Config class (weights, paths, thresholds)
│       ├── helpers.py             # normalize_skill(), calculate_experience_years()
│       └── email_sender.py        # EmailSender (SMTP TLS/SSL)
├── ui/
│   └── app.py                     # Streamlit web application (3 tabs)
├── data/
│   ├── skills_database.json       # 100+ curated skills across 8 categories
│   ├── sample_resumes/
│   │   ├── sample_resume_1.txt    # Jane Smith – Full Stack Engineer (6 yrs)
│   │   └── sample_resume_2.txt    # Michael Chen – ML Engineer (4.5 yrs)
│   └── sample_jobs/
│       ├── job_description_1.txt  # Senior Full Stack Engineer (5 yrs req.)
│       └── job_description_2.txt  # Machine Learning Engineer (3 yrs req.)
├── tests/
│   ├── test_parser.py
│   ├── test_extractor.py
│   ├── test_matcher.py
│   ├── test_ocr_processor.py
│   └── test_evaluation.py         # 42 tests for src/evaluation/
├── notebooks/
│   └── exploration.ipynb
├── temp/                           # Temporary files (auto-created, not committed)
├── main.py                         # CLI entry point
├── evaluate.py                     # Standalone evaluation runner
├── generate_report.py              # Mid-semester DOCX report generator
├── requirements.txt
├── setup.py
├── QUICKSTART.md
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10 or higher** (tested on Python 3.13.1)
- **pip** and a virtual environment (recommended)
- **Tesseract OCR** – required only for scanned image / OCR input
  - Windows: download from https://github.com/UB-Mannheim/tesseract/wiki
  - Add the Tesseract install directory to your `PATH`

### Step 1: Navigate to the Project

```powershell
cd "c:\Users\sobasu\Downloads\BITS Pilani\4th Sem\dissertation"
```

### Step 2: Create and Activate Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Download spaCy Model (Optional)

spaCy enables advanced lemmatisation and NER. The system runs fully without it via regex fallbacks.

```bash
python -m spacy download en_core_web_sm
```

### Step 5: Verify Installation

```bash
python -c "import streamlit, PyPDF2, docx, sklearn; print('Core dependencies OK')"
```

---

## ⚡ Quick Start

### Run the Web Application

```bash
streamlit run ui/app.py
```

Opens at `http://localhost:8501`

### Run the CLI Demo

```bash
python main.py
```

Select option `2` for a CLI walkthrough using the bundled sample data.

### Run Evaluation Metrics

```bash
python evaluate.py
```

Prints a formatted Precision / Recall / F1 table for all 7 extraction modules plus matching metrics. Add `--json` for machine-readable output, `--save` to write `temp/eval_results.json`.

### Generate the Mid-Semester Report

```bash
python generate_report.py
```

Produces `Mid_Semester_Report_AI_Resume_Screening.docx` in the project root with live evaluation results embedded.

---

## 📖 How to Use

### Processing Mode

The **Resume Analysis** tab contains a **Processing Mode** toggle (Single / Batch). Choose the mode before starting.

### Single Mode

#### Tab 1 – Resume Analysis

1. Choose **Upload File** (PDF / DOCX / TXT / image) or **Paste Text**.
2. Click **Parse Resume**.
3. Review extracted entities: name, email, phone, skills, experience timeline, education, certifications.

> For scanned PDFs or images the system automatically routes input through `OCRProcessor` (requires Tesseract).

#### Tab 2 – Job Matching

1. Paste or upload a job description.
2. Click **Parse Job Description** to extract required skills, preferred skills, and experience requirement.
3. Click **Calculate Match Score**.
4. Review the overall score (0–100 %), match band, matched skills (green), missing skills (red), and recommendation.

#### Tab 3 – Gap Analysis

1. Complete Tabs 1 and 2 first (parsed objects are held in session state).
2. Click **Generate Gap Analysis**.
3. Review skill coverage percentages, experience gap, improvement suggestions, and learning path.
4. **Download Report** to save the text report locally.
5. **Send Email** to dispatch the gap report to the candidate (configure SMTP in the sidebar).

### Batch Mode

#### Tab 1 – Resume Analysis (Batch)

1. Upload up to **10 resumes** (PDF / DOCX / TXT / image).
2. Click **Parse All Resumes**. A progress bar tracks parsing.
3. Parsed results appear in collapsible expanders — one per resume, showing the same extracted entities as single mode.
4. Failed parses display the error inline.

#### Tab 2 – Job Matching (Batch)

1. Upload or paste **one job description** (left panel).
2. Click **Parse Job Description**.
3. Click **Calculate Match Scores** to match all parsed resumes against the JD.
4. Results appear in collapsible expanders — one per resume — with score, decision (Accept / Review / Reject), matched/missing skills.

#### Tab 3 – Gap Analysis (Batch)

1. Click **Generate All Gap Analyses**.
2. Each resume–JD pair gets its own collapsible section with skill coverage, experience analysis, improvement suggestions, priority areas, PDF report download, and email provision.

### Email Configuration (Sidebar)

1. Select provider (Gmail, Gmail SSL, Outlook/Hotmail, Yahoo, Custom).
2. Enter sender email and password / App Password.
3. Click **🔌 Test Connection** to verify credentials before sending.
4. Click **💾 Save Config** to persist settings for the session.

---

## 📊 Evaluation

The `src/evaluation/` package provides quantitative assessment of the system against hand-labelled ground truth.

### Extraction Metrics (7 modules, 2 annotated resumes)

| Module | Precision | Recall | F1-Score |
|---|---|---|---|
| Email Extraction | 100 % | 100 % | 1.0000 |
| Phone Extraction | 100 % | 50 % | 0.6667 |
| Name Extraction | 100 % | 100 % | 1.0000 |
| Skill Extraction | ~84 % | ~88 % | ~0.86 |
| Experience Extraction | 0 % | 0 % | 0.0000 |
| Education Extraction | 0 % | 0 % | 0.0000 |
| Certification Extraction | ~29 % | ~50 % | ~0.36 |
| **Macro Average** | **~59 %** | **~55 %** | **~0.57** |

> Experience and Education show 0.00 F1 because the structured date/title regex patterns do not match the section-bullet format used in the sample resumes. These modules are flagged as priority improvement areas.

Run `python evaluate.py` to reproduce these numbers live.

### Matching Metrics (4 resume–job pairs)

| Metric | Value |
|---|---|
| Shortlisting Accuracy | 100 % (4 / 4 correct) |
| Mean Absolute Error (MAE) | ~14 pts |
| Spearman's ρ | 1.000 |

Ground truth and recruiter decisions are defined in `src/evaluation/ground_truth.py`.

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Modules

```bash
pytest tests/test_parser.py -v
pytest tests/test_extractor.py -v
pytest tests/test_matcher.py -v
pytest tests/test_ocr_processor.py -v
pytest tests/test_evaluation.py -v     # 42 tests for src/evaluation/
```

### Generate Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
```

Open `htmlcov/index.html` to browse line-level coverage.

---

## 🏗️ Architecture

### Layers

```
┌────────────────────────────────────────────────────┐
│  UI Layer        – Streamlit (ui/app.py)           │
├────────────────────────────────────────────────────┤
│  Data Input     – ResumeParser / JDParser          │
│                   TextPreprocessor                 │
├────────────────────────────────────────────────────┤
│  Extraction     – EntityExtractor                  │
│                   SkillExtractor                   │
│                   ExperienceExtractor              │
│                   OCRProcessor                     │
├────────────────────────────────────────────────────┤
│  Matching       – JobMatcher                       │
│                   SimilarityCalculator             │
├────────────────────────────────────────────────────┤
│  Analysis       – GapAnalyzer                      │
│                   ReportGenerator                  │
│                   EmailSender                      │
├────────────────────────────────────────────────────┤
│  Evaluation     – ExtractionEvaluator              │
│                   MatchingEvaluator                │
├────────────────────────────────────────────────────┤
│  Data & Utils   – skills_database.json             │
│                   Config / helpers                 │
└────────────────────────────────────────────────────┘
```

### Matching Score Composition

```
Overall Score = 0.50 × Skill Score
              + 0.30 × Experience Score
              + 0.20 × Education Score

Skill Score       = 0.70 × (matched required / total required)
                  + 0.30 × (matched preferred / total preferred)
Experience Score  = min(1.0, candidate_years / required_years)
Education Score   = 1.0  if degree matches requirement
                    0.5  if any degree present
                    0.0  if no education data found
```

---

## 🛠️ Technologies Used

| Category | Library / Tool | Version |
|---|---|---|
| Web Framework | Streamlit | ≥ 1.28 |
| PDF Parsing | PyPDF2 | ≥ 3.0 |
| DOCX Parsing | python-docx | ≥ 1.1 |
| OCR Engine | Tesseract + pytesseract | ≥ 0.3.10 |
| Image Processing | Pillow | ≥ 10.0 |
| Image Processing | OpenCV (cv2) | ≥ 4.8 |
| Scanned PDF → Image | pdf2image | ≥ 1.16 |
| NLP (optional) | spaCy (en_core_web_sm) | ≥ 3.7 |
| NLP (core) | NLTK + Python `re` | ≥ 3.8 |
| ML / Similarity | scikit-learn | ≥ 1.3 |
| Data processing | pandas, numpy | ≥ 2.1 / ≥ 1.24 |
| Visualisation | matplotlib, seaborn | ≥ 3.8 / ≥ 0.13 |
| Report export | reportlab | ≥ 4.0 |
| Email | smtplib (stdlib) | built-in |
| Testing | pytest + pytest-cov | ≥ 7.4 |

---

## 📊 Sample Data

### Sample Resumes

| File | Candidate | Role | Experience |
|---|---|---|---|
| `sample_resume_1.txt` | Jane Smith | Full Stack Engineer | 6.0 yrs |
| `sample_resume_2.txt` | Michael Chen | ML Engineer | 4.5 yrs |

### Sample Job Descriptions

| File | Role | Required Experience |
|---|---|---|
| `job_description_1.txt` | Senior Full Stack Engineer | 5 yrs |
| `job_description_2.txt` | Machine Learning Engineer | 3 yrs |

### Skills Database (`data/skills_database.json`)

100+ entries across 8 categories: programming languages, web technologies, databases, cloud & DevOps, data science & ML, tools, soft skills, and other technical skills.

---

## 🐛 Troubleshooting

### spaCy model not found

```
OSError: [E050] Can't find model 'en_core_web_sm'
```

spaCy is **optional** — the system falls back to regex automatically. To enable it:

```bash
python -m spacy download en_core_web_sm
```

### Module import errors

```
ModuleNotFoundError: No module named 'streamlit'
```

```bash
pip install -r requirements.txt
```

### OCR not working

```
pytesseract.pytesseract.TesseractNotFoundError
```

Install Tesseract and add it to `PATH`:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- The `OCRProcessor` surfaces a clear error in the UI when Tesseract is absent.

### Port already in use

```bash
streamlit run ui/app.py --server.port 8502
```

### Email connection timeout (WinError 10060)

1. Try **Outlook/Hotmail** – usually bypasses corporate firewall restrictions
2. Switch to **Gmail SSL (port 465)**
3. Connect via a mobile hotspot
4. Allow outbound SMTP through Windows Firewall (run as Administrator):

```powershell
New-NetFirewallRule -DisplayName "Allow SMTP 587" -Direction Outbound -Protocol TCP -LocalPort 587 -Action Allow
New-NetFirewallRule -DisplayName "Allow SMTP 465" -Direction Outbound -Protocol TCP -LocalPort 465 -Action Allow
```

### Gmail authentication failed

Gmail requires an **App Password**, not your regular password:

1. Enable 2-Step Verification in Google Account
2. Go to Security → 2-Step Verification → App passwords
3. Generate a password for "Mail"
4. Use the 16-character generated password in the application

---

## 🔭 Future Work

1. **BERT / Sentence-BERT semantic matching** – replace keyword overlap with embedding-based similarity to handle synonyms and paraphrasing
2. **Experience and Education extractor improvements** – update regex patterns to handle section-bullet format (currently 0.00 F1)
3. **Expanded evaluation dataset** – annotate 50+ resumes across multiple domains for a robust benchmark

---

## 👤 Author

**Suhas Obasu**  
Student ID: 2024MT03102  
M.Tech WILP – 4th Semester  
BITS Pilani | Dissertation CCZG628T

---

## 📝 License

This project is licensed under the MIT License.
