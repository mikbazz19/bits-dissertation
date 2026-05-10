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
3. **Intelligent Matching** – Score candidate profiles against job requirements using a configurable weighted algorithm
4. **Gap Analysis** – Identify skill and experience gaps with prioritised improvement suggestions
5. **Evaluation** – Quantitatively measure extraction and matching quality using Precision, Recall, F1-Score, and Spearman's ρ

---

## ✨ Features

### Multi-Format Resume & JD Parsing

- PDF, Microsoft Word (DOCX), and plain text (TXT) via `ResumeParser`
- Scanned images (PNG, JPG, JPEG, TIFF, BMP, WebP) and image-heavy PDFs via OCR (`OCRProcessor` + Tesseract)
- Direct text paste in the web UI
- Graceful UTF-8 / Latin-1 encoding fallback for text files
- Automatic document-type detection — rejects a JD uploaded in the resume slot and vice versa

### Information Extraction

- **Personal entities** – name (first-line heuristic with Unicode/international name support), email (RFC-5321 regex), phone (international formats)
- **Skills** – word-boundary regex matching against a curated JSON database of 100+ technologies across 8 categories
- **Work experience** – structured date-range parsing with total years calculation; fallback to summary-sentence extraction
- **Education** – 18 degree keywords (B.Tech, M.Tech, MBA, PhD, BSc, …), year, and institution
- **Certifications** – AWS Certified, PMP, CISSP, CompTIA, and section-list extraction

### Job Description Analysis

- Section segmentation (responsibilities, requirements, skills, education, experience) via keyword look-ahead
- Required and preferred skill extraction
- Years-of-experience parsing via `(\d+)\+?\s*years?\s*of\s*experience` patterns

### Matching Algorithm

- **Configurable weighted composite score** — default: Skills 50 % · Experience 30 % · Education 20 %
- Weights are fully user-adjustable via sidebar sliders (must sum to exactly 100 %)
- Hard filters: minimum experience check, mandatory skill threshold, overqualification guard (buffer: 3 years)
- Confidence factor penalises sparse/minimal resumes
- Decision bands: **Accept** (≥ 75 %), **Review** (60–74 %), **Reject** (< 60 %)
- Match levels: Excellent (≥ 80 %), Good (60–79 %), Fair (40–59 %), Poor (< 40 %)
- `SimilarityCalculator` provides Jaccard, Cosine, SequenceMatcher, and Overlap (Szymkiewicz–Simpson) metrics
- `fuzzy_match()` catches near-synonyms (e.g., "ML" ↔ "Machine Learning") at a configurable threshold
- **Explainability panel** – "Why this score?" expander shows per-component contribution table, confidence factor detail, and full matched/missing skills breakdown
- **Fairness note** – scores within ±5 pts of a threshold display a human-review advisory

### Gap Analysis

- Required and preferred skill coverage percentages
- Experience shortfall in years (domain-aware)
- Education requirement check
- `_generate_suggestions()` maps gaps to top-5 missing skills, internship advice, and online programme recommendations
- `generate_learning_path()` pairs missing skills with resource type, platform, and estimated duration

### Report Generation

- **Screening Report** – full candidate vs. job summary
- **Gap Report** – skill coverage and priority action items
- **Comparison Report** – multi-candidate ranking table
- PDF download per candidate in both single and batch mode

### Web Application (Streamlit)

- **Four-tab layout** — Resume Analysis · Job Matching · Gap Analysis · Analytics
- **Single / Batch processing mode** selectable from the Resume Analysis tab
  - **Single mode** – one resume against one JD (full workflow across all tabs)
  - **Batch mode** – upload up to 10 resumes against one JD; results in collapsible expanders
- File upload + text paste input
- Session state preserves parsed objects across tab switches
- Progress bars during batch parsing, matching, and gap analysis
- PDF report download and email dispatch per candidate
- Email dispatch via SMTP (TLS / SSL)
- Temporary uploaded files written to `temp/` and deleted after parsing
- **Light / Dark theme toggle** in sidebar
- **Candidate ranking leaderboard** (batch mode) — sorted by score with 🥇🥈🥉 medals

### Analytics Dashboard

- **Single Mode — Analytics tab** ("Resume Analytics & Quality Score"):
  - Resume Quality Score (0–100, graded A–F) with component breakdown:
    Completeness · Content Quality · Skills Presentation · Experience Quality
  - Profile summary, key metrics (total skills, experience years, contact completeness)
  - Skills-by-Category interactive bar chart (Plotly, theme-aware)
  - Strengths list; "Areas for Improvement" section shown only when weaknesses exist
  - Match Analysis Insights when a JD has also been matched
- **Batch Mode — Analytics tab** ("Batch Analytics & Insights"):
  - Overview metrics: total candidates, average score, accepted count, rejected count
  - Score distribution histogram
  - Decision breakdown donut chart (Accept / Review / Reject)
  - Experience level distribution bar chart
  - Score and experience statistics (mean, median, min, max)
  - Most common skills across all candidates
  - Candidate Comparison Table (all scores, colour-coded decisions) — exportable to CSV
  - Common skill gaps across the batch
- All Plotly charts adapt to Light / Dark theme automatically

### Configurable Matching Weights (Sidebar)

- Three independent sliders: Skills, Experience, Education (each 0–100 %, step 5)
- Live validation: ✅ green confirmation when sum = 100 %, ⚠️ warning/error otherwise
- Changing weights automatically invalidates cached match results, prompting a re-run

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
│   │   ├── entity_extractor.py    # Name (Unicode-aware), email, phone, education, certs
│   │   ├── skill_extractor.py     # Skill extraction + categorisation
│   │   ├── experience_extractor.py# Work history, date parsing, total years
│   │   ├── ocr_processor.py       # Tesseract OCR + OpenCV pre-processing
│   │   ├── resume_parser.py       # High-level resume parse orchestrator
│   │   └── parser.py              # Extraction-layer helpers, IMAGE_EXTENSIONS
│   ├── matching/                   # Matching engine
│   │   ├── job_matcher.py         # Weighted composite scorer (configurable weights)
│   │   └── similarity.py          # Jaccard, Cosine, SequenceMatcher, Overlap
│   ├── analysis/                   # Analysis and reporting
│   │   ├── gap_analyzer.py        # Skill/experience/education gap analysis
│   │   ├── report_generator.py    # Screening, gap, comparison reports (PDF)
│   │   ├── analytics.py           # ScreeningAnalytics (batch + single resume)
│   │   └── resume_quality_scorer.py  # ResumeQualityScorer (0-100 score, grade, suggestions)
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
│       ├── config.py              # Config class (default weights, thresholds, paths)
│       ├── helpers.py             # normalize_skill(), calculate_experience_years()
│       └── email_sender.py        # EmailSender (SMTP TLS/SSL)
├── ui/
│   └── app.py                     # Streamlit web application (4 tabs, single+batch mode)
├── data/
│   ├── skills_database.json       # 100+ curated skills across 8 categories
│   ├── sample_resumes/            # 20+ test resumes (TXT, PDF, DOCX, images, edge cases)
│   └── sample_jobs/               # 20+ test job descriptions (TXT, PDF, DOCX, images)
├── tests/
│   ├── test_parser.py
│   ├── test_extractor.py
│   ├── test_matcher.py
│   ├── test_ocr_processor.py
│   ├── test_evaluation.py         # 42 tests for src/evaluation/
│   └── test_analytics.py          # Tests for analytics and quality scorer
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
  - Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki
  - Add the Tesseract install directory (e.g. `C:\Program Files\Tesseract-OCR`) to your `PATH`

### Step 1: Navigate to the Project

```powershell
cd "c:\Users\sobasu\Downloads\BITS Pilani\4th Sem\dissertation"
```

### Step 2: Create and Activate Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you see a script-execution policy error, first run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```

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
python -c "import streamlit, PyPDF2, docx, sklearn, plotly; print('Core dependencies OK')"
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

Prints a formatted Precision / Recall / F1 table for all 7 extraction modules plus matching metrics.  
Add `--json` for machine-readable output, `--save` to write `temp/eval_results.json`.

### Generate the Mid-Semester Report

```bash
python generate_report.py
```

Produces `Mid_Semester_Report_AI_Resume_Screening.docx` in the project root with live evaluation results embedded.

---

## 📖 How to Use

### Processing Mode

The **Resume Analysis** tab contains a **Processing Mode** radio button (Single / Batch).  
Select the mode before uploading files.

| Mode | Analytics tab |
|---|---|
| Single | Resume Analytics & Quality Score |
| Batch | Batch Analytics & Insights |

---

### Single Mode

#### Tab 1 – Resume Analysis

1. Choose **Upload File** (PDF / DOCX / TXT / PNG / JPG / TIFF / BMP / WebP) or **Paste Text**.
2. Click **Parse Resume**.
3. Review extracted entities: name, email, phone, skills, experience timeline, education, certifications.

> For scanned PDFs or images the system automatically routes input through `OCRProcessor` (requires Tesseract installed and on `PATH`).

#### Tab 2 – Job Matching

1. Upload or paste a job description.
2. Click **Parse Job Description** to extract required skills, preferred skills, and experience requirement.
3. Click **Calculate Match Score**.
4. Review the overall score, eligibility checks, decision (Accept / Review / Reject) with reason, matched/missing skills, and recommendation.
5. Expand **"🔍 Why this score?"** for a per-component contribution table, confidence factor detail, and full skills breakdown.
6. If the score is within ±5 % of a threshold, a **⚖️ fairness note** advises human review.

#### Tab 3 – Gap Analysis

1. Complete Tabs 1 and 2 first (parsed objects are held in session state).
2. Click **Generate Gap Analysis**.
3. Review skill coverage percentages, experience gap, improvement suggestions, priority areas, and learning path.
4. Click **Download PDF Report** to save a formatted PDF locally.
5. Click **Send Email** to dispatch the gap report to the candidate (configure SMTP in the sidebar first).

#### Tab 4 – Analytics (Single Mode)

1. Requires a parsed resume (Tab 1).
2. **Resume Quality Score** (0–100, graded A–F) with component scores (each out of 25):
   - Completeness — contact info, skills count, education, experience presence
   - Content Quality — quantified achievements, action verbs, word count
   - Skills Presentation — skill count and category variety
   - Experience Quality — role progression, descriptions, duration
3. Profile Analytics: summary, total skills, experience years, contact completeness %.
4. Skills-by-Category interactive bar chart.
5. If a match has been run: Match Analysis Insights with score metrics, strengths, and areas for improvement (areas only shown when weaknesses exist).

---

### Batch Mode

#### Tab 1 – Resume Analysis (Batch)

1. Upload up to **10 resumes** (PDF / DOCX / TXT / image formats supported).
2. Click **Parse All Resumes**. A progress bar tracks parsing.
3. Parsed results appear in collapsible expanders — one per resume, showing extracted entities.
4. Files that cannot be parsed display the error inline; others continue normally.

#### Tab 2 – Job Matching (Batch)

1. Upload or paste **one job description** in the left panel; click **Parse Job Description**.
2. Click **Calculate Match Scores** to match all parsed resumes against the JD.
3. A **🏆 Candidate Ranking** leaderboard appears first — all candidates sorted by score with 🥇🥈🥉 medals for top 3.
4. Individual collapsible expanders below show full match details (including "Why this score?" and fairness notes).

#### Tab 3 – Gap Analysis (Batch)

1. Click **Generate All Gap Analyses**.
2. Each candidate gets a collapsible section with skill coverage, experience analysis, improvement suggestions, priority areas, PDF download, and email provision.

#### Tab 4 – Analytics (Batch Mode)

1. Requires batch matches computed (Tab 2).
2. Overview metrics: total candidates, average score, accepted, rejected.
3. Visualisations: score distribution histogram, decision breakdown donut chart, experience distribution bar chart.
4. Statistics: score and experience mean / median / min / max.
5. Most common skills across all candidates.
6. **Candidate Comparison Table** with colour-coded decisions — click **📥 Download Comparison Table (CSV)** to export.
7. Common skill gaps across the batch.

---

### Sidebar Controls

| Section | Description |
|---|---|
| 🌙 / ☀️ Theme toggle | Switch between Dark (default) and Light mode |
| ℹ️ About | Collapsible — system feature overview |
| 📖 How to Use | Collapsible — quick workflow steps |
| ⚖️ Matching Weights | Collapsible (open by default) — Skills / Experience / Education sliders; must sum to 100 % |
| 📧 Email Configuration | Collapsible — SMTP provider, credentials, Test Connection, Save Config |

> **Note:** Changing matching weights automatically invalidates existing match results. Re-run "Calculate Match Score" after adjusting weights.

---

## 📊 Evaluation

The `src/evaluation/` package provides quantitative assessment against hand-labelled ground truth.

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
pytest tests/test_analytics.py -v      # Analytics and quality scorer tests
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
│                   Single mode + Batch mode         │
│                   4-tab layout, theme, sidebar     │
├────────────────────────────────────────────────────┤
│  Data Input     – ResumeParser / JDParser          │
│                   TextPreprocessor                 │
│                   OCRProcessor (images/scanned)    │
├────────────────────────────────────────────────────┤
│  Extraction     – EntityExtractor (Unicode-aware)  │
│                   SkillExtractor                   │
│                   ExperienceExtractor              │
├────────────────────────────────────────────────────┤
│  Matching       – JobMatcher (configurable weights)│
│                   SimilarityCalculator             │
│                   Hard filters + Confidence factor │
├────────────────────────────────────────────────────┤
│  Analysis       – GapAnalyzer                      │
│                   ReportGenerator (PDF)            │
│                   ScreeningAnalytics               │
│                   ResumeQualityScorer              │
│                   EmailSender                      │
├────────────────────────────────────────────────────┤
│  Evaluation     – ExtractionEvaluator              │
│                   MatchingEvaluator                │
├────────────────────────────────────────────────────┤
│  Data & Utils   – skills_database.json             │
│                   Config (weights, thresholds)     │
│                   helpers                          │
└────────────────────────────────────────────────────┘
```

### Default Matching Score Composition

Default weights (50 / 30 / 20) are configurable via the sidebar sliders:

```
Overall Score = w_skills  × Skill Score
              + w_exp     × Experience Score
              + w_edu     × Education Score
              (w_skills + w_exp + w_edu = 1.0)

Skill Score       = 0.70 × (matched required / total required)
                  + 0.30 × (matched preferred / total preferred)
Experience Score  = min(1.0, candidate_years / required_years)
Education Score   = 1.0  if degree matches requirement
                    0.5  if any degree present
                    0.0  if no education data found

Final Score = Overall Score × Confidence Factor
```

### Decision Thresholds

| Score | Decision |
|---|---|
| ≥ 75 % | ✅ Accept |
| 60 – 74 % | 🔍 Review |
| < 60 % | ❌ Reject |

Hard filter failure (minimum experience not met, insufficient mandatory skills, or overqualification by > 3 years) → automatic **Reject** regardless of weighted score.

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
| Interactive charts | plotly | ≥ 5.17 |
| Static visualisation | matplotlib, seaborn | ≥ 3.8 / ≥ 0.13 |
| Report / PDF export | reportlab | ≥ 4.0 |
| Excel export | openpyxl | ≥ 3.1 |
| Email | smtplib (stdlib) | built-in |
| Testing | pytest + pytest-cov | ≥ 7.4 |

---

## 📊 Sample Data

### Sample Resumes (`data/sample_resumes/`)

| File | Description |
|---|---|
| `sample_resume_1.txt` | Jane Smith – Full Stack Engineer (6 yrs) |
| `sample_resume_2.txt` | Michael Chen – ML Engineer (4.5 yrs) |
| `resume_3_fresher.txt` | Fresh graduate, minimal experience |
| `resume_4_minimal_sparse.txt` | Very sparse / minimal content |
| `resume_5_unicode_international.txt` | International candidate with Unicode name |
| `resume_6_career_changer.txt` | Mid-career domain change |
| `resume_7_overqualified.txt` | Candidate significantly overqualified |
| `resume_8_no_sections_freeform.txt` | Unstructured freeform text |
| `resume_9_employment_gaps.txt` | Candidate with employment gaps |
| `resume_10_skills_heavy_devops.txt` | DevOps-heavy skill set |
| `resume_docx.docx` | DOCX format test |
| `resume_native_pdf.pdf` | Natively-created (selectable text) PDF |
| `resume_scanned_jpg.jpg` | Scanned image — OCR required |
| `resume_scanned_png.png` | Scanned image — OCR required |
| `resume_scanned_tiff.tiff` | Scanned image — OCR required |
| `resume_empty.txt` | Empty file edge case |
| `resume_whitespace_only.txt` | Whitespace-only edge case |
| `resume_very_long.txt` | Very long resume edge case |
| `resume_corrupt.pdf` | Corrupt PDF edge case |

### Sample Job Descriptions (`data/sample_jobs/`)

| File | Role |
|---|---|
| `job_description_1.txt` | Senior Full Stack Engineer (5 yrs req.) |
| `job_description_2.txt` | Machine Learning Engineer (3 yrs req.) |
| `job_description_3_entry_level.txt` | Entry-level position |
| `job_description_4_minimal.txt` | Minimal requirements |
| `job_description_5_niche_embedded.txt` | Niche embedded systems role |
| `job_description_6_data_analyst.txt` | Data Analyst |
| `job_description_7_devops.txt` | DevOps Engineer |
| `job_description_8_backend_engineer.txt` | Backend Engineer |
| `job_description_9_senior_backend.txt` | Senior Backend Engineer |
| `job_description_10_devops_platform.txt` | DevOps Platform Engineer |
| `job_description_docx.docx` | DOCX format test |
| `job_description_native_pdf.pdf` | Natively-created PDF test |
| `job_description_scanned_jpg.jpg` | Scanned image — OCR required |

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

### Virtual environment activation blocked

```
cannot be loaded because running scripts is disabled on this system
```

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Port already in use

```bash
streamlit run ui/app.py --server.port 8502
```

### Match results disappeared after adjusting sidebar sliders

Expected behaviour. Changing matching weights invalidates cached results to prevent stale scores. Re-click **Calculate Match Score** (single mode) or **Calculate Match Scores** (batch mode).

### Email connection timeout (WinError 10060)

1. Try **Outlook/Hotmail** – usually bypasses corporate firewall restrictions
2. Switch to **Port 465 (SSL)** in the Connection Type dropdown
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
