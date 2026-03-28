"""
Document parser — routes files to the correct extractor backend.
Now includes OCR support for image-based and scanned-PDF resumes.
"""

from pathlib import Path
from typing import Union

# Lazy import so OCR dependencies are optional
_ocr_processor = None


def _get_ocr_processor():
    """Return a shared OCRProcessor instance (lazy init)."""
    global _ocr_processor
    if _ocr_processor is None:
        from src.extraction.ocr_processor import OCRProcessor
        _ocr_processor = OCRProcessor()
    return _ocr_processor


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}


def parse_document(file_path: Union[str, Path]) -> str:
    """
    Parse a resume or job-description document and return its text content.

    Supports:
      - Plain text  (.txt)
      - PDF         (.pdf)  — both native text and scanned/image-only
      - Word        (.docx)
      - Images      (.png, .jpg, .jpeg, .tiff, .bmp, .webp)

    Args:
        file_path: Path to the document.

    Returns:
        Extracted text string.
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    # --- Image file: always use OCR ---
    if suffix in IMAGE_EXTENSIONS:
        return _get_ocr_processor().extract_text(file_path)

    # --- PDF: try native extraction first, fall back to OCR ---
    if suffix == '.pdf':
        text = _extract_native_pdf_text(file_path)
        if _is_meaningful_text(text):
            return text
        # Scanned PDF — fall back to OCR
        import logging
        logging.getLogger(__name__).info(
            f"{file_path.name}: native PDF text empty, falling back to OCR."
        )
        return _get_ocr_processor().extract_text(file_path)

    # --- Plain text / Word / etc. ---
    return _extract_plain_text(file_path)


def _extract_native_pdf_text(file_path: Path) -> str:
    """Extract embedded text from a PDF using PyMuPDF / pdfminer (existing logic)."""
    # ...existing code...
    return ""


def _extract_plain_text(file_path: Path) -> str:
    """Read a plain-text file."""
    # ...existing code...
    return file_path.read_text(encoding='utf-8', errors='replace')


def _is_meaningful_text(text: str, min_chars: int = 50) -> bool:
    """Return True if the extracted text contains enough real content."""
    return len(text.strip()) >= min_chars