"""
OCR Processor module for extracting text from image-based resumes and documents.
Supports image files (PNG, JPG, JPEG, TIFF, BMP) and scanned PDFs.
"""

import os
import re
import logging
from pathlib import Path
from typing import Union, List, Optional

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Handles OCR processing for image-based resumes and scanned documents.
    Preprocesses images to improve OCR accuracy before text extraction.
    """

    SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}
    SUPPORTED_PDF_FORMAT = {'.pdf'}

    # ------------------------------------------------------------------
    # Section heading patterns for resume parsing
    # ------------------------------------------------------------------
    SECTION_PATTERNS = {
        "education": re.compile(
            r'(?i)^\s*(education|academic\s+background|academic\s+qualifications?'
            r'|qualifications?|degrees?|schooling)\s*:?\s*$',
            re.MULTILINE
        ),
        "certifications": re.compile(
            r'(?i)^\s*(certifications?|certificates?|professional\s+certifications?'
            r'|licenses?\s*&?\s*certifications?|accreditations?)\s*:?\s*$',
            re.MULTILINE
        ),
        "skills": re.compile(
            r'(?i)^\s*(skills?|technical\s+skills?|core\s+competenc(y|ies)'
            r'|technologies|tools?\s*&?\s*technologies?)\s*:?\s*$',
            re.MULTILINE
        ),
        "experience": re.compile(
            r'(?i)^\s*((?:professional\s+)?experience|work\s+(?:history|experience)'
            r'|employment(?:\s+history)?|career\s+(?:history|summary))\s*:?\s*$',
            re.MULTILINE
        ),
    }

    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'eng', dpi: int = 300):
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "OCR dependencies not installed. "
                "Run: pip install pytesseract Pillow opencv-python"
            )

        # ── Windows: auto-detect Tesseract if not given explicitly ──
        tesseract_cmd = tesseract_cmd or os.getenv("TESSERACT_CMD")
        if not tesseract_cmd and os.name == 'nt':
            default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(default):
                tesseract_cmd = default

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.lang = lang
        self.dpi = dpi
        self._verify_tesseract()

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def _verify_tesseract(self) -> None:
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR verified and available.")
        except pytesseract.TesseractNotFoundError:
            raise EnvironmentError(
                "Tesseract OCR is not installed or not found in PATH.\n"
                "Install it from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Then add  C:\\Program Files\\Tesseract-OCR  to your system PATH,\n"
                "or set TESSERACT_CMD in your .env file."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """Extract raw text from an image or scanned PDF via OCR."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix in self.SUPPORTED_IMAGE_FORMATS:
            logger.info(f"Processing image file: {file_path.name}")
            return self._extract_from_image(file_path)

        if suffix in self.SUPPORTED_PDF_FORMAT:
            logger.info(f"Processing scanned PDF file: {file_path.name}")
            return self._extract_from_scanned_pdf(file_path)

        raise ValueError(
            f"Unsupported file format '{suffix}'. "
            f"Supported: {self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_PDF_FORMAT}"
        )

    def extract_sections(self, file_path: Union[str, Path]) -> dict:
        """
        Extract text AND split it into labelled resume sections.

        Returns a dict with keys:
            raw_text, education, certifications, skills, experience
        All section values default to '' if the section is not found.
        """
        raw = self.extract_text(file_path)
        sections = self._split_into_sections(raw)
        sections["raw_text"] = raw
        return sections

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        suffix = Path(file_path).suffix.lower()
        return suffix in (self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_PDF_FORMAT)

    # ------------------------------------------------------------------
    # Section Splitter
    # ------------------------------------------------------------------

    def _split_into_sections(self, text: str) -> dict:
        """
        Locate each known section heading in the OCR text and slice out
        the content that follows it, up to the next heading.

        Handles common OCR artefacts:
          - extra spaces inside headings  ("E D U C A T I O N")
          - lower/mixed case              ("Education:", "education")
          - missing separator lines
        """
        result = {k: "" for k in self.SECTION_PATTERNS}

        # Normalise spaced-out letters from OCR  e.g. "E D U C A T I O N"
        normalised = re.sub(
            r'\b([A-Z])\s(?=[A-Z]\b)', r'\1', text
        )

        # Find all section heading positions
        hits: List[tuple] = []   # (start_pos, section_key)
        for key, pattern in self.SECTION_PATTERNS.items():
            for m in pattern.finditer(normalised):
                hits.append((m.start(), m.end(), key))

        if not hits:
            logger.warning("No section headings detected in OCR output.")
            return result

        # Sort by position in document
        hits.sort(key=lambda x: x[0])

        # Slice content between consecutive headings
        for i, (start, end, key) in enumerate(hits):
            next_start = hits[i + 1][0] if i + 1 < len(hits) else len(normalised)
            section_text = normalised[end:next_start].strip()
            # If same section appears twice, concatenate
            result[key] = (result[key] + "\n" + section_text).strip() \
                if result[key] else section_text

        return result

    # ------------------------------------------------------------------
    # Image Extraction
    # ------------------------------------------------------------------

    def _extract_from_image(self, file_path: Path) -> str:
        image = Image.open(file_path)
        preprocessed = self._preprocess_image(image)
        # Use LSTM engine + page-segmentation mode 3 (fully automatic)
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(preprocessed, lang=self.lang,
                                           config=custom_config)
        return self._clean_text(text)

    def _extract_from_scanned_pdf(self, file_path: Path) -> str:
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError(
                "pdf2image is required for scanned PDF support. "
                "Run: pip install pdf2image  "
                "Also install poppler: https://poppler.freedesktop.org/"
            )

        pages: List[Image.Image] = convert_from_path(str(file_path), dpi=self.dpi)
        logger.info(f"Converted PDF to {len(pages)} page(s) at {self.dpi} DPI.")

        extracted_pages: List[str] = []
        for i, page in enumerate(pages, start=1):
            logger.debug(f"  OCR processing page {i}/{len(pages)} …")
            preprocessed = self._preprocess_image(page)
            custom_config = r'--oem 3 --psm 3'
            page_text = pytesseract.image_to_string(preprocessed, lang=self.lang,
                                                    config=custom_config)
            extracted_pages.append(self._clean_text(page_text))

        return "\n\n".join(extracted_pages)

    # ------------------------------------------------------------------
    # Image Preprocessing Pipeline
    # ------------------------------------------------------------------

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocessing pipeline to maximise OCR accuracy:
          1.  Normalise colour mode (handles CMYK / palette / RGBA)
          2.  Convert to grayscale
          3.  Upscale images narrower than 1 800 px
          4.  Deskew via OpenCV minAreaRect
          5.  Denoise with bilateral filter
          6.  Adaptive Gaussian threshold (binarisation)
          7.  Morphological opening to remove noise specks
          8.  Sharpen + contrast boost (PIL)
        """
        # 1. Normalise
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        # 2. Grayscale
        image = image.convert('L')

        # 3. Upscale — raised to 1800 for better character resolution
        min_width = 1800
        if image.width < min_width:
            scale = min_width / image.width
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.LANCZOS)

        # 4-7: OpenCV pipeline
        cv_img = np.array(image)
        cv_img = self._deskew(cv_img)
        cv_img = cv2.bilateralFilter(cv_img, d=9, sigmaColor=75, sigmaSpace=75)
        cv_img = cv2.adaptiveThreshold(
            cv_img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=15, C=4          # slightly larger block for scanned docs
        )
        # Morphological opening: remove isolated noise pixels
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cv_img = cv2.morphologyEx(cv_img, cv2.MORPH_OPEN, kernel)

        # 8. PIL finishing
        image = Image.fromarray(cv_img)
        image = image.filter(ImageFilter.SHARPEN)
        image = ImageEnhance.Contrast(image).enhance(2.0)

        return image

    @staticmethod
    def _deskew(image: np.ndarray) -> np.ndarray:
        """Correct skew using minAreaRect on foreground pixel coordinates."""
        inverted = cv2.bitwise_not(image)
        coords = np.column_stack(np.where(inverted > 0))
        if coords.size == 0:
            return image

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle

        if abs(angle) < 0.5:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        logger.debug(f"Image deskewed by {angle:.2f}°")
        return deskewed

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Post-process raw Tesseract output:
          - Remove non-printable characters (keep tab, LF, CR, space–~)
          - Collapse 3+ consecutive blank lines → 2
          - Fix common Tesseract digit/letter confusions in section headings
        """
        # Remove non-printable
        text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Common OCR heading fixes
        ocr_fixes = {
            r'\bEDUCAT[Il1]ON\b': 'EDUCATION',
            r'\bCERTIF[Il1]CAT[Il1]ONS?\b': 'CERTIFICATIONS',
            r'\bEXPER[Il1]ENCE\b': 'EXPERIENCE',
            r'\bSK[Il1]LLS?\b': 'SKILLS',
        }
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text.strip()