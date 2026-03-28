"""
OCR Processor module for extracting text from image-based resumes and documents.
Supports image files (PNG, JPG, JPEG, TIFF, BMP) and scanned PDFs.
"""

import os
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

    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'eng', dpi: int = 300):
        """
        Initialize OCRProcessor.

        Args:
            tesseract_cmd: Optional path to tesseract executable.
                           e.g. r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' on Windows
            lang: Language for Tesseract OCR (default: 'eng')
            dpi: DPI resolution for PDF-to-image conversion (default: 300)
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "OCR dependencies not installed. Run: pip install pytesseract Pillow opencv-python"
            )

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.lang = lang
        self.dpi = dpi
        self._verify_tesseract()

    def _verify_tesseract(self) -> None:
        """Verify that Tesseract is installed and accessible."""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR verified and available.")
        except pytesseract.TesseractNotFoundError:
            raise EnvironmentError(
                "Tesseract OCR is not installed or not found in PATH.\n"
                "Install it from: https://github.com/tesseract-ocr/tesseract\n"
                "On Ubuntu/Debian: sudo apt install tesseract-ocr\n"
                "On macOS: brew install tesseract\n"
                "On Windows: https://github.com/UB-Mannheim/tesseract/wiki"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from an image or scanned PDF file using OCR.

        Args:
            file_path: Path to the image or PDF file.

        Returns:
            Extracted text as a string.

        Raises:
            ValueError: If the file format is not supported.
            FileNotFoundError: If the file does not exist.
        """
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
            f"Supported formats: "
            f"{self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_PDF_FORMAT}"
        )

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """Return True if the file format is supported by the OCR processor."""
        suffix = Path(file_path).suffix.lower()
        return suffix in (self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_PDF_FORMAT)

    # ------------------------------------------------------------------
    # Image Processing
    # ------------------------------------------------------------------

    def _extract_from_image(self, file_path: Path) -> str:
        """Load, preprocess, and OCR a single image file."""
        image = Image.open(file_path)
        preprocessed = self._preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed, lang=self.lang)
        return self._clean_text(text)

    def _extract_from_scanned_pdf(self, file_path: Path) -> str:
        """Convert a scanned PDF to images, then OCR each page."""
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
            page_text = pytesseract.image_to_string(preprocessed, lang=self.lang)
            extracted_pages.append(self._clean_text(page_text))

        return "\n\n".join(extracted_pages)

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply a preprocessing pipeline to improve OCR accuracy:
          1. Convert to RGB (handles CMYK / palette modes)
          2. Convert to grayscale
          3. Upscale small images
          4. Deskew via OpenCV
          5. Denoise (bilateral filter)
          6. Adaptive thresholding (binarization)
          7. Sharpen
          8. Boost contrast
        """
        # 1. Normalise colour mode
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        # 2. Grayscale
        image = image.convert('L')

        # 3. Upscale if image is too small (helps Tesseract)
        min_width = 1200
        if image.width < min_width:
            scale = min_width / image.width
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.LANCZOS)

        # 4-6: Switch to OpenCV for deskew / denoise / threshold
        cv_img = np.array(image)

        cv_img = self._deskew(cv_img)
        cv_img = cv2.bilateralFilter(cv_img, d=9, sigmaColor=75, sigmaSpace=75)
        cv_img = cv2.adaptiveThreshold(
            cv_img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11, C=2
        )

        # 7-8: Back to PIL for sharpening / contrast
        image = Image.fromarray(cv_img)
        image = image.filter(ImageFilter.SHARPEN)
        image = ImageEnhance.Contrast(image).enhance(2.0)

        return image

    @staticmethod
    def _deskew(image: np.ndarray) -> np.ndarray:
        """
        Detect and correct skew in a grayscale numpy image using the
        Hough line transform approach.
        """
        # Invert so text pixels are white for line detection
        inverted = cv2.bitwise_not(image)
        coords = np.column_stack(np.where(inverted > 0))
        if coords.size == 0:
            return image

        angle = cv2.minAreaRect(coords)[-1]
        # minAreaRect returns angles in [-90, 0); convert to actual skew
        if angle < -45:
            angle = 90 + angle

        if abs(angle) < 0.5:          # negligible skew — skip rotation
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(
            image, rotation_matrix, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        logger.debug(f"Image deskewed by {angle:.2f}°")
        return deskewed

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Post-process raw Tesseract output:
          - Strip leading/trailing whitespace
          - Collapse 3+ consecutive blank lines to 2
          - Remove non-printable characters
        """
        import re
        # Remove non-printable except newline/tab
        text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()