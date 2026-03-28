"""
Unit and integration tests for the OCRProcessor module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sample_resume_text():
    """Return the text content of the OCR sample resume."""
    resume_path = Path("data/sample_resumes/sample_resume_ocr.txt")
    if resume_path.exists():
        return resume_path.read_text(encoding="utf-8")
    return (
        "MICHAEL TORRES\nSenior Data Engineer\n"
        "Python SQL Spark Kafka Snowflake AWS"
    )


@pytest.fixture(scope="module")
def sample_job_text():
    """Return the text content of the OCR sample job description."""
    job_path = Path("data/sample_jobs/job_description_ocr.txt")
    if job_path.exists():
        return job_path.read_text(encoding="utf-8")
    return (
        "Senior Data Engineer\n"
        "Python SQL Spark Kafka Snowflake AWS Airflow Docker Kubernetes"
    )


@pytest.fixture
def mock_ocr_processor():
    """
    Return a patched OCRProcessor that never calls Tesseract,
    so tests run without the binary installed in CI.
    """
    with patch("src.extraction.ocr_processor.TESSERACT_AVAILABLE", True), \
         patch("pytesseract.get_tesseract_version", return_value="5.0.0"), \
         patch("pytesseract.image_to_string") as mock_ocr:
        mock_ocr.return_value = "Mocked OCR text output"
        from src.extraction.ocr_processor import OCRProcessor
        processor = OCRProcessor.__new__(OCRProcessor)
        processor.lang = "eng"
        processor.dpi = 300
        yield processor, mock_ocr


# ---------------------------------------------------------------------------
# OCRProcessor unit tests
# ---------------------------------------------------------------------------

class TestOCRProcessorInit:
    def test_raises_if_tesseract_unavailable(self):
        with patch("src.extraction.ocr_processor.TESSERACT_AVAILABLE", False):
            from src.extraction.ocr_processor import OCRProcessor
            with pytest.raises(ImportError, match="OCR dependencies not installed"):
                OCRProcessor()

    def test_raises_if_tesseract_not_in_path(self):
        with patch("src.extraction.ocr_processor.TESSERACT_AVAILABLE", True), \
             patch("pytesseract.get_tesseract_version",
                   side_effect=Exception("not found")):
            from src.extraction.ocr_processor import OCRProcessor
            with pytest.raises(Exception):
                OCRProcessor()


class TestSupportedFormats:
    def test_image_extensions_supported(self, mock_ocr_processor):
        processor, _ = mock_ocr_processor
        for ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            assert processor.is_supported_format(f"resume{ext}") is True

    def test_pdf_supported(self, mock_ocr_processor):
        processor, _ = mock_ocr_processor
        assert processor.is_supported_format("resume.pdf") is True

    def test_unsupported_extension(self, mock_ocr_processor):
        processor, _ = mock_ocr_processor
        assert processor.is_supported_format("resume.docx") is False
        assert processor.is_supported_format("resume.txt") is False

    def test_extract_text_raises_for_unsupported(self, mock_ocr_processor, tmp_path):
        processor, _ = mock_ocr_processor
        fake_file = tmp_path / "resume.xyz"
        fake_file.write_text("hello")
        with pytest.raises(ValueError, match="Unsupported file format"):
            processor.extract_text(fake_file)

    def test_extract_text_raises_for_missing_file(self, mock_ocr_processor, tmp_path):
        processor, _ = mock_ocr_processor
        with pytest.raises(FileNotFoundError):
            processor.extract_text(tmp_path / "nonexistent.png")


class TestTextCleaning:
    """Tests for the static _clean_text helper."""

    def _clean(self, text):
        from src.extraction.ocr_processor import OCRProcessor
        return OCRProcessor._clean_text(text)

    def test_strips_leading_trailing_whitespace(self):
        assert self._clean("  hello  ") == "hello"

    def test_collapses_excessive_blank_lines(self):
        result = self._clean("line1\n\n\n\n\nline2")
        assert "\n\n\n" not in result

    def test_removes_non_printable_characters(self):
        result = self._clean("hello\x00world\x01")
        assert "\x00" not in result
        assert "\x01" not in result

    def test_preserves_normal_newlines(self):
        result = self._clean("line1\nline2\n\nline3")
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result


class TestImagePreprocessing:
    """Tests for the image preprocessing pipeline."""

    def test_preprocess_returns_pil_image(self, mock_ocr_processor):
        pytest.importorskip("PIL")
        pytest.importorskip("cv2")
        from PIL import Image
        processor, _ = mock_ocr_processor
        img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
        result = processor._preprocess_image(img)
        assert result is not None

    def test_preprocess_upscales_small_image(self, mock_ocr_processor):
        pytest.importorskip("PIL")
        pytest.importorskip("cv2")
        from PIL import Image
        processor, _ = mock_ocr_processor
        small_img = Image.new("L", (400, 500), color=200)
        result = processor._preprocess_image(small_img)
        assert result.width >= 1200

    def test_preprocess_handles_rgba_mode(self, mock_ocr_processor):
        pytest.importorskip("PIL")
        pytest.importorskip("cv2")
        from PIL import Image
        processor, _ = mock_ocr_processor
        rgba_img = Image.new("RGBA", (1200, 1600), color=(255, 255, 255, 255))
        # Should not raise
        result = processor._preprocess_image(rgba_img)
        assert result is not None


# ---------------------------------------------------------------------------
# Integration-style tests using sample data files
# ---------------------------------------------------------------------------

class TestSampleDataFiles:
    """Validate that sample data files exist and contain expected keywords."""

    def test_sample_resume_ocr_file_exists(self):
        path = Path("data/sample_resumes/sample_resume_ocr.txt")
        assert path.exists(), f"Missing sample file: {path}"

    def test_sample_job_ocr_file_exists(self):
        path = Path("data/sample_jobs/job_description_ocr.txt")
        assert path.exists(), f"Missing sample file: {path}"

    def test_sample_resume_contains_key_fields(self, sample_resume_text):
        required = ["MICHAEL TORRES", "Python", "Spark", "AWS", "Snowflake"]
        for keyword in required:
            assert keyword in sample_resume_text, (
                f"Expected keyword '{keyword}' not found in OCR sample resume."
            )

    def test_sample_job_contains_key_fields(self, sample_job_text):
        required = ["Data Engineer", "Python", "Spark", "Kafka", "Snowflake"]
        for keyword in required:
            assert keyword in sample_job_text, (
                f"Expected keyword '{keyword}' not found in OCR sample job description."
            )

    def test_resume_skills_overlap_with_job(self, sample_resume_text, sample_job_text):
        """At least some skills from the resume should appear in the job description."""
        skills = ["Python", "SQL", "Spark", "Kafka", "Snowflake",
                  "Airflow", "AWS", "Docker", "Kubernetes", "dbt"]
        resume_skills = {s for s in skills if s in sample_resume_text}
        job_skills    = {s for s in skills if s in sample_job_text}
        overlap = resume_skills & job_skills
        assert len(overlap) >= 5, (
            f"Expected ≥5 overlapping skills, found {len(overlap)}: {overlap}"
        )


# ---------------------------------------------------------------------------
# Parser routing tests
# ---------------------------------------------------------------------------

class TestParserOCRRouting:
    """Verify that parse_document routes image files through OCR."""

    def test_image_file_routed_to_ocr(self, tmp_path):
        pytest.importorskip("PIL")
        from PIL import Image

        img_path = tmp_path / "resume.png"
        img = Image.new("RGB", (1200, 1600), color=(255, 255, 255))
        img.save(img_path)

        with patch("src.extraction.parser._get_ocr_processor") as mock_getter:
            mock_proc = MagicMock()
            mock_proc.extract_text.return_value = "Extracted OCR text"
            mock_getter.return_value = mock_proc

            from src.extraction import parser
            result = parser.parse_document(img_path)

            mock_proc.extract_text.assert_called_once_with(img_path)
            assert result == "Extracted OCR text"

    def test_scanned_pdf_falls_back_to_ocr(self, tmp_path):
        """Native PDF extraction returns empty → OCR fallback is used."""
        pdf_path = tmp_path / "scanned.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 empty")

        with patch("src.extraction.parser._extract_native_pdf_text", return_value=""), \
             patch("src.extraction.parser._get_ocr_processor") as mock_getter:
            mock_proc = MagicMock()
            mock_proc.extract_text.return_value = "OCR fallback text"
            mock_getter.return_value = mock_proc

            from src.extraction import parser
            result = parser.parse_document(pdf_path)

            mock_proc.extract_text.assert_called_once_with(pdf_path)
            assert result == "OCR fallback text"

    def test_text_pdf_does_not_use_ocr(self, tmp_path):
        """PDFs with embedded text should NOT trigger OCR."""
        pdf_path = tmp_path / "native.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 with text")

        with patch("src.extraction.parser._extract_native_pdf_text",
                   return_value="This PDF has plenty of native text already."), \
             patch("src.extraction.parser._get_ocr_processor") as mock_getter:
            from src.extraction import parser
            parser.parse_document(pdf_path)
            mock_getter.assert_not_called()