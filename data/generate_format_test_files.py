"""
generate_format_test_files.py
─────────────────────────────
Generates test data files in various formats to exercise the parser/OCR pipeline:

  Format Coverage Files (data/format_tests/):
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ File                              │ Scenario                               │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │ resume_native_pdf.pdf             │ Native/searchable PDF (PyPDF2 path)     │
  │ job_description_native_pdf.pdf    │ Native PDF – job description            │
  │ resume_docx.docx                  │ Word (.docx) format                     │
  │ job_description_docx.docx         │ Word (.docx) – job description          │
  │ resume_scanned_png.png            │ Image PNG → OCR path                    │
  │ job_description_scanned_png.png   │ Image PNG JD → OCR path                 │
  │ resume_scanned_jpg.jpg            │ Image JPEG → OCR path                   │
  │ job_description_scanned_jpg.jpg   │ Image JPEG JD → OCR path                │
  │ resume_scanned_tiff.tiff          │ TIFF → OCR path (common for scans)      │
  │ job_description_scanned_tiff.tiff │ TIFF JD → OCR path                      │
  │ resume_empty.txt                  │ Completely empty resume (edge case)     │
  │ job_description_empty.txt         │ Completely empty JD (edge case)         │
  │ resume_whitespace_only.txt        │ Only whitespace / blank lines           │
  │ job_description_whitespace_only.txt│ Only whitespace / blank lines – JD     │
  │ resume_very_long.txt              │ Extremely long resume (stress test)     │
  │ job_description_very_long.txt     │ Extremely long JD (stress test)         │
  │ resume_repeated_skills.txt        │ Same skill listed many ways (dedup)     │
  │ job_description_repeated_reqs.txt │ Same requirement listed many ways (dedup│
  │ resume_unsupported.rtf            │ Unsupported format (.rtf) – error path  │
  │ job_description_unsupported.rtf   │ Unsupported JD format (.rtf)            │
  │ resume_unsupported.xls            │ Unsupported format (.xls) – error path  │
  │ job_description_unsupported.xls   │ Unsupported JD format (.xls)            │
  │ resume_corrupt.pdf                │ Corrupted/invalid PDF bytes             │
  │ job_description_corrupt.pdf       │ Corrupted/invalid PDF bytes – JD        │
  └─────────────────────────────────────────────────────────────────────────────┘

Usage:
    python generate_format_test_files.py

Requirements (already in requirements.txt):
    reportlab, python-docx, Pillow
"""

import os
import sys
from pathlib import Path

# ── Output directory ───────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "format_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Shared resume / JD content
# ─────────────────────────────────────────────────────────────────────────────

RESUME_TEXT = """\
ALEX JORDAN
alex.jordan@testmail.com | +1-555-100-2000

SUMMARY
Software Engineer with 5 years of experience in Python and cloud infrastructure.
Specialising in REST APIs, microservices, and PostgreSQL.

EXPERIENCE
Software Engineer — CloudSoft Inc., Seattle, WA        (2020 – Present)
  • Built REST APIs with FastAPI serving 1M+ requests/day
  • Managed PostgreSQL databases and wrote complex query optimisations
  • Technologies: Python, FastAPI, PostgreSQL, AWS, Docker, Kubernetes

Junior Developer — DevAgency, Austin, TX               (2018 – 2020)
  • Developed and maintained Django web applications
  • Wrote unit tests with pytest; coverage raised to 90%
  • Technologies: Python, Django, MySQL, Git

EDUCATION
B.Sc. in Computer Science — University of Texas at Austin (2018)

SKILLS
Python, FastAPI, Django, Flask, PostgreSQL, MySQL, MongoDB, Redis,
AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes, Git, pytest, REST API

CERTIFICATIONS
AWS Certified Developer – Associate (2022)
"""

JD_TEXT = """\
Software Engineer – Backend
OpenCloud Inc. | Austin, TX (Hybrid)

ABOUT THE ROLE
We are looking for a Backend Software Engineer to join our platform team.

REQUIRED SKILLS
- Python (3+ years): FastAPI, Django or Flask
- SQL databases: PostgreSQL or MySQL
- Cloud: AWS (EC2, S3, Lambda)
- Docker and Kubernetes basics
- Git version control
- REST API design

PREFERRED SKILLS
- Redis or other caching layers
- CI/CD pipelines (GitHub Actions, Jenkins)
- Monitoring (Prometheus, Grafana)

EDUCATION
Bachelor's in Computer Science or related field required.

EXPERIENCE
Minimum 3 years professional software engineering experience.
"""


# ─────────────────────────────────────────────────────────────────────────────
# 1. Native / searchable PDFs  (reportlab)
# ─────────────────────────────────────────────────────────────────────────────

def create_pdf(file_path: Path, text: str, title: str = "Document") -> None:
    """Create a native, text-searchable PDF using reportlab."""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_LEFT

        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title=title,
        )
        styles = getSampleStyleSheet()
        mono = ParagraphStyle(
            "Mono",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            alignment=TA_LEFT,
        )

        story = []
        for line in text.splitlines():
            safe = (
                line.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
            )
            story.append(Paragraph(safe if safe.strip() else "&nbsp;", mono))
            story.append(Spacer(1, 1))

        doc.build(story)
        print(f"  [OK] {file_path.name}")
    except ImportError:
        print("  [SKIP] reportlab not installed — skipping PDF generation.")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Word (.docx)  (python-docx)
# ─────────────────────────────────────────────────────────────────────────────

def create_docx(file_path: Path, text: str) -> None:
    """Create a Word (.docx) document from plain text."""
    try:
        from docx import Document
        from docx.shared import Pt

        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Courier New"
        style.font.size = Pt(9)

        for line in text.splitlines():
            doc.add_paragraph(line)

        doc.save(str(file_path))
        print(f"  [OK] {file_path.name}")
    except ImportError:
        print("  [SKIP] python-docx not installed — skipping DOCX generation.")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Image files (PNG, JPEG, TIFF)  — Pillow renders text → raster image
# ─────────────────────────────────────────────────────────────────────────────

def create_image_resume(file_path: Path, text: str, fmt: str = "PNG") -> None:
    """Render resume text onto a white canvas and save as raster image (for OCR testing)."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # A4 at 150 dpi ≈ 1240 × 1754
        width, height = 1240, 1754
        margin = 60
        line_height = 20

        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Try to use a monospace font; fall back to default
        try:
            font = ImageFont.truetype("cour.ttf", 14)   # Windows Courier
        except OSError:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
            except OSError:
                font = ImageFont.load_default()

        y = margin
        for line in text.splitlines():
            if y + line_height > height - margin:
                break  # avoid overflow — use multi-page in production
            draw.text((margin, y), line, fill=(0, 0, 0), font=font)
            y += line_height

        # Add a subtle noise band to simulate scanner imperfection
        import random
        for _ in range(300):
            x = random.randint(0, width - 1)
            yy = random.randint(0, height - 1)
            draw.point((x, yy), fill=(200, 200, 200))

        save_kwargs = {}
        if fmt.upper() == "TIFF":
            save_kwargs = {"compression": "tiff_lzw"}
        elif fmt.upper() in ("JPEG", "JPG"):
            save_kwargs = {"quality": 85}

        img.save(str(file_path), format=fmt, **save_kwargs)
        print(f"  [OK] {file_path.name}")
    except ImportError:
        print("  [SKIP] Pillow not installed — skipping image generation.")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Plain-text edge-case files
# ─────────────────────────────────────────────────────────────────────────────

def create_text_file(file_path: Path, content: str) -> None:
    file_path.write_text(content, encoding="utf-8")
    print(f"  [OK] {file_path.name}")


VERY_LONG_JD = """\
Software Engineer – Backend (Extended Requirements Listing)
MegaCorp Inc. | Remote

ABOUT THE ROLE
This intentionally verbose job description is used to stress-test the parser's
handling of large JD documents. Contains many requirement sections.

""" + "\n".join(
    f"REQUIREMENT GROUP {i}\n"
    f"  - Experience with technology stack {i} (Python, Java, or C++)\n"
    f"  - Familiarity with cloud platform {i} (AWS, GCP, or Azure)\n"
    f"  - {i + 1}+ years professional experience in area {i}\n"
    for i in range(1, 51)
) + """
CORE REQUIRED SKILLS
""" + ", ".join([f"RequiredSkill-{i}" for i in range(1, 151)]) + """

EDUCATION
Bachelor's degree in Computer Science or related field required.

EXPERIENCE
Minimum 3 years professional software engineering experience.
"""

REPEATED_REQS_JD = """\
Software Engineer – Backend
DuplicateCo | Remote

ABOUT THE ROLE
This JD intentionally lists the same requirements in multiple ways to test
the deduplication logic in the job description parser.

REQUIRED SKILLS
Python, python, PYTHON, Python 3, Python3, Py
JavaScript, javascript, JS, js, ECMAScript
SQL, sql, SQL Server, MySQL, MySQL 8, MYSQL
AWS, Amazon Web Services, Amazon AWS, aws
Docker, docker, DOCKER, Docker Container
React, ReactJS, React.js, react.js

JOB REQUIREMENTS
- Must know Python (3+ years)
- Proficient in python development
- Experience with PYTHON web frameworks
- SQL experience required
- Must be familiar with SQL Server or MySQL
- AWS deployment experience (Cloud: Amazon Web Services, aws)

EXPERIENCE
Minimum 2 years in a software engineering role.

EDUCATION
Bachelor's in Computer Science or equivalent.
"""

VERY_LONG_RESUME = """\
ALEX LONGSWORTH
alex.longsworth@bigmail.com | (555) 999-1234

SUMMARY
An intentionally very long resume used to stress-test the parser's handling of
large documents. Contains repeated blocks of experience and skills sections.

""" + "\n".join(
    f"EXPERIENCE ENTRY {i}\n"
    f"Company {i}, City, Country  (201{i % 10} – 201{(i+2) % 10})\n"
    f"  - Worked extensively with Python, Java, or C++ on project iteration {i}.\n"
    f"  - Deployed services on AWS, GCP, or Azure environment {i}.\n"
    f"  - Managed team of {i + 1} engineers. Improved velocity by {(i * 7) % 50 + 10}%%.\n"
    for i in range(1, 51)
) + """
SKILLS
""" + ", ".join([f"Skill-{i}" for i in range(1, 201)]) + """

EDUCATION
B.Sc. Computer Science — Test University (2010)
M.Sc. Software Engineering — Test University (2012)
"""

REPEATED_SKILLS_RESUME = """\
CHRIS DUPLICATE
chris.dup@test.com | 555-777-8888

SUMMARY
This resume intentionally lists the same skills in multiple ways to test
the deduplication logic in the skill extractor.

SKILLS
Python, python, PYTHON, Python 3, Python3, Py
JavaScript, javascript, JS, js, ECMAScript
SQL, sql, SQL Server, MySQL, MySQL 8, MYSQL
AWS, Amazon Web Services, Amazon AWS, aws
Docker, docker, DOCKER, Docker Container
React, ReactJS, React.js, react.js

EXPERIENCE
Developer — FakeCo (2020–Present)
  Technologies: Python, JavaScript, SQL, AWS, Docker, React

EDUCATION
B.Sc. Computer Science — Some University (2020)
"""


# ─────────────────────────────────────────────────────────────────────────────
# 5. Unsupported and corrupt files
# ─────────────────────────────────────────────────────────────────────────────

def create_unsupported_rtf(file_path: Path, content_label: str = "JOHN DOE") -> None:
    """Create a minimal .rtf file (unsupported by the parser — should raise ValueError)."""
    rtf_content = (
        r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Courier;}}"
        rf"{{\f0 {content_label}\line test@test.com\line Python SQL AWS\par}}"
    )
    file_path.write_text(rtf_content, encoding="ascii")
    print(f"  [OK] {file_path.name}  ← unsupported format (.rtf)")


def create_unsupported_xls(file_path: Path) -> None:
    """Create a dummy .xls file (unsupported — should raise ValueError)."""
    file_path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1FAKE_XLS_CONTENT")
    print(f"  [OK] {file_path.name}  ← unsupported format (.xls)")


def create_corrupt_pdf(file_path: Path) -> None:
    """Create a file with .pdf extension but corrupt/invalid PDF content."""
    corrupt_bytes = b"%PDF-1.4\nThis is deliberately corrupted PDF content.\nNot a valid PDF.\n\x00\xff"
    file_path.write_bytes(corrupt_bytes)
    print(f"  [OK] {file_path.name}  ← corrupt/invalid PDF")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\nGenerating format test files into: {OUTPUT_DIR}\n")

    # --- Native PDFs ---
    print("[1/9] Native text PDFs")
    create_pdf(OUTPUT_DIR / "resume_native_pdf.pdf", RESUME_TEXT, "Resume – Alex Jordan")
    create_pdf(OUTPUT_DIR / "job_description_native_pdf.pdf", JD_TEXT, "Job Description – Backend Engineer")

    # --- Word .docx ---
    print("[2/9] Word documents (.docx)")
    create_docx(OUTPUT_DIR / "resume_docx.docx", RESUME_TEXT)
    create_docx(OUTPUT_DIR / "job_description_docx.docx", JD_TEXT)

    # --- Image files (OCR path) ---
    print("[3/9] PNG images (simulated scan) — resume + JD pair")
    create_image_resume(OUTPUT_DIR / "resume_scanned_png.png", RESUME_TEXT, "PNG")
    create_image_resume(OUTPUT_DIR / "job_description_scanned_png.png", JD_TEXT, "PNG")

    print("[4/9] JPEG images (simulated scan) — resume + JD pair")
    create_image_resume(OUTPUT_DIR / "resume_scanned_jpg.jpg", RESUME_TEXT, "JPEG")
    create_image_resume(OUTPUT_DIR / "job_description_scanned_jpg.jpg", JD_TEXT, "JPEG")

    print("[5/9] TIFF images (simulated scan) — resume + JD pair")
    create_image_resume(OUTPUT_DIR / "resume_scanned_tiff.tiff", RESUME_TEXT, "TIFF")
    create_image_resume(OUTPUT_DIR / "job_description_scanned_tiff.tiff", JD_TEXT, "TIFF")

    # --- Plain text edge cases ---
    print("[6/9] Plain-text edge cases — resume + JD pairs")
    create_text_file(OUTPUT_DIR / "resume_empty.txt", "")
    create_text_file(OUTPUT_DIR / "job_description_empty.txt", "")
    create_text_file(OUTPUT_DIR / "resume_whitespace_only.txt", "   \n\n\t   \n   ")
    create_text_file(OUTPUT_DIR / "job_description_whitespace_only.txt", "   \n\n\t   \n   ")
    create_text_file(OUTPUT_DIR / "resume_very_long.txt", VERY_LONG_RESUME)
    create_text_file(OUTPUT_DIR / "job_description_very_long.txt", VERY_LONG_JD)
    create_text_file(OUTPUT_DIR / "resume_repeated_skills.txt", REPEATED_SKILLS_RESUME)
    create_text_file(OUTPUT_DIR / "job_description_repeated_reqs.txt", REPEATED_REQS_JD)

    # --- Unsupported formats ---
    print("[7/9] Unsupported format files — resume + JD pairs")
    create_unsupported_rtf(OUTPUT_DIR / "resume_unsupported.rtf", "JOHN DOE")
    create_unsupported_rtf(OUTPUT_DIR / "job_description_unsupported.rtf", "Backend Engineer Role")
    create_unsupported_xls(OUTPUT_DIR / "resume_unsupported.xls")
    create_unsupported_xls(OUTPUT_DIR / "job_description_unsupported.xls")

    # --- Corrupt / invalid PDF ---
    print("[8/9] Corrupt PDFs — resume + JD pair")
    create_corrupt_pdf(OUTPUT_DIR / "resume_corrupt.pdf")
    create_corrupt_pdf(OUTPUT_DIR / "job_description_corrupt.pdf")

    # --- Summary ---
    print("\n[9/9] Summary")
    files = sorted(OUTPUT_DIR.iterdir())
    print(f"  Total files created: {len(files)}")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"    {f.name:<45}  {size_kb:>8.1f} KB")

    print("\nDone. Use these files to test format handling, OCR fallback,")
    print("error/exception paths, and edge-case content parsing.\n")


if __name__ == "__main__":
    main()
