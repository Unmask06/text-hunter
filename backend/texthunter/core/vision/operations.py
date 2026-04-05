"""PDF rendering and text association operations for P&ID processing."""

from __future__ import annotations

import logging
import re

import fitz  # PyMuPDF
import numpy as np

from .opencv import SymbolMatch

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------


def render_pdf_pages(
    pdf_bytes: bytes,
    dpi: int = 150,
    page_numbers: list[int] | None = None,
) -> list[tuple[int, np.ndarray]]:
    """Render PDF pages to numpy BGR images using PyMuPDF.

    Args:
        pdf_bytes: Raw PDF file bytes.
        dpi: Rendering resolution (72–300). 150 gives ~1240x1754 for A4.
        page_numbers: 1-based page numbers to render. None renders all pages.

    Returns:
        List of (1-based page number, BGR image array) tuples.

    """
    results: list[tuple[int, np.ndarray]] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        total = doc.page_count
        pages_to_render = page_numbers if page_numbers else list(range(1, total + 1))

        for page_no in pages_to_render:
            if page_no < 1 or page_no > total:
                logger.warning("Page %d out of range (1-%d), skipping", page_no, total)
                continue
            page = doc[page_no - 1]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3
            )
            # PyMuPDF returns RGB; convert to BGR for OpenCV
            import cv2

            bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            results.append((page_no, bgr))

    return results


# ---------------------------------------------------------------------------
# Text association
# ---------------------------------------------------------------------------


def find_nearby_text(
    match: SymbolMatch,
    page_text: str,
    radius_px: int = 80,
) -> list[str]:
    """Associate P&ID tag strings near a detected symbol.

    When pre-extracted text is available (from the existing PDF worker),
    this function searches for ISA-format instrument tags (e.g. FT-101,
    LV-203) in a window of text around the symbol's page position.

    NOTE: Full spatial text association requires per-word bounding box data
    from PyMuPDF's get_text("words") API. This implementation returns a
    best-effort tag list by scanning the full page text for tag patterns.
    A future enhancement should pass word-level bbox data for precise matching.

    Args:
        match: Detected symbol with (x, y, width, height).
        page_text: Full page text as a string.
        radius_px: Unused in text-only mode (reserved for spatial matching).

    Returns:
        List of unique tag strings found on the same page.

    """
    tag_pattern = re.compile(
        r"\b[A-Z]{1,4}[-_]?\d{3,5}[A-Z]?\b",
    )
    tags = list(set(tag_pattern.findall(page_text)))
    return tags[:10]  # limit to 10 nearest candidates
