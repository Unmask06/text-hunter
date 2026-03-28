"""P&ID symbol detection and image processing utilities using OpenCV and PyMuPDF."""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass, field
from io import BytesIO

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SymbolMatch:
    """A single symbol detection result on a page."""

    symbol_name: str
    page: int
    x: int
    y: int
    width: int
    height: int
    confidence: float
    scale: float = 1.0
    angle_deg: float = 0.0
    associated_tags: list[str] = field(default_factory=list)


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
        dpi: Rendering resolution (72–300). 150 gives ~1240×1754 for A4.
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
                logger.warning("Page %d out of range (1–%d), skipping", page_no, total)
                continue
            page = doc[page_no - 1]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3
            )
            # PyMuPDF returns RGB; convert to BGR for OpenCV
            bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            results.append((page_no, bgr))

    return results


# ---------------------------------------------------------------------------
# Image encode / decode helpers
# ---------------------------------------------------------------------------


def image_to_base64_png(image: np.ndarray) -> str:
    """Encode a BGR numpy image to a base64-encoded PNG string."""
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Failed to encode image to PNG")
    return base64.b64encode(buffer.tobytes()).decode("ascii")


def base64_to_image(b64_str: str) -> np.ndarray:
    """Decode a base64-encoded PNG/JPEG string to a BGR numpy image."""
    raw = base64.b64decode(b64_str)
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode base64 image")
    return img


def pil_to_numpy(pil_image: Image.Image) -> np.ndarray:
    """Convert a PIL Image to a BGR numpy array."""
    return cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Legend template extraction
# ---------------------------------------------------------------------------


def extract_legend_templates(
    image: np.ndarray,
    bounding_boxes: list[tuple[int, int, int, int]],
) -> list[np.ndarray]:
    """Crop user-annotated bounding boxes from a legend image.

    Args:
        image: BGR legend page image.
        bounding_boxes: List of (x, y, w, h) in pixel coordinates.

    Returns:
        List of cropped BGR template images.
    """
    templates = []
    h, w = image.shape[:2]
    for x, y, bw, bh in bounding_boxes:
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w, x + bw)
        y2 = min(h, y + bh)
        crop = image[y1:y2, x1:x2]
        if crop.size > 0:
            templates.append(crop)
        else:
            logger.warning("Empty crop for box (%d,%d,%d,%d), skipping", x, y, bw, bh)
    return templates


def auto_segment_legend_grid(
    image: np.ndarray,
    min_symbol_area: int = 400,
    max_symbol_area: int = 40000,
) -> list[tuple[tuple[int, int, int, int], np.ndarray]]:
    """Automatically find discrete symbols in a structured legend grid.

    Uses morphological operations and contour detection to isolate symbol
    regions. Returns results ordered left-to-right, top-to-bottom.

    Args:
        image: BGR legend page image.
        min_symbol_area: Minimum pixel area for a candidate symbol region.
        max_symbol_area: Maximum pixel area for a candidate symbol region.

    Returns:
        List of ((x, y, w, h), cropped_image) tuples.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Invert (symbols are typically dark on white)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate to connect nearby strokes into a single blob
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilated = cv2.dilate(binary, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if min_symbol_area <= area <= max_symbol_area:
            crop = image[y : y + h, x : x + w]
            results.append(((x, y, w, h), crop))

    # Sort left-to-right, top-to-bottom (by row then column)
    results.sort(key=lambda r: (r[0][1] // 60, r[0][0]))
    return results


# ---------------------------------------------------------------------------
# Symbol detection (multi-scale template matching)
# ---------------------------------------------------------------------------


def _apply_clahe(gray: np.ndarray) -> np.ndarray:
    """Apply CLAHE contrast normalisation for consistent matching."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def detect_symbol_in_page(
    page_image: np.ndarray,
    template: np.ndarray,
    symbol_name: str,
    page_number: int,
    threshold: float = 0.75,
    scale_range: tuple[float, float] = (0.7, 1.3),
    scale_steps: int = 7,
    angle_steps: list[float] | None = None,
) -> list[SymbolMatch]:
    """Find all instances of a template symbol in a page image.

    Uses multi-scale (and optionally multi-angle) template matching with
    non-maximum suppression to remove duplicates.

    Args:
        page_image: BGR image of the full P&ID page.
        template: BGR image of the symbol to search for.
        symbol_name: Label for this symbol type.
        page_number: 1-based page number for result metadata.
        threshold: Minimum normalised cross-correlation score (0–1).
        scale_range: (min_scale, max_scale) relative to template size.
        scale_steps: Number of scale increments to test.
        angle_steps: Rotation angles in degrees to test. None = no rotation.

    Returns:
        List of SymbolMatch objects sorted by confidence descending.
    """
    gray_page = _apply_clahe(cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY))
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    scales = np.linspace(scale_range[0], scale_range[1], scale_steps)
    angles = angle_steps if angle_steps else [0.0]

    raw_matches: list[SymbolMatch] = []

    ph, pw = page_image.shape[:2]
    th, tw = template.shape[:2]

    for scale in scales:
        new_w = max(1, int(tw * scale))
        new_h = max(1, int(th * scale))

        if new_w > pw or new_h > ph:
            continue

        resized = cv2.resize(gray_template, (new_w, new_h))

        for angle in angles:
            if angle != 0.0:
                center = (new_w / 2, new_h / 2)
                rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    resized, rot_mat, (new_w, new_h),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE,
                )
            else:
                rotated = resized

            result = cv2.matchTemplate(gray_page, rotated, cv2.TM_CCOEFF_NORMED)
            ys, xs = np.where(result >= threshold)

            for x, y in zip(xs, ys):
                score = float(result[y, x])
                raw_matches.append(
                    SymbolMatch(
                        symbol_name=symbol_name,
                        page=page_number,
                        x=int(x),
                        y=int(y),
                        width=new_w,
                        height=new_h,
                        confidence=round(score, 4),
                        scale=round(float(scale), 3),
                        angle_deg=float(angle),
                    )
                )

    return suppress_overlapping_matches(raw_matches)


def suppress_overlapping_matches(
    matches: list[SymbolMatch],
    iou_threshold: float = 0.3,
) -> list[SymbolMatch]:
    """Non-maximum suppression to remove duplicate / overlapping detections.

    Args:
        matches: Raw detection list (may contain many overlapping hits).
        iou_threshold: IoU above which the lower-confidence box is removed.

    Returns:
        Filtered list sorted by confidence descending.
    """
    if not matches:
        return []

    # Sort by confidence descending
    sorted_matches = sorted(matches, key=lambda m: m.confidence, reverse=True)
    kept: list[SymbolMatch] = []

    for candidate in sorted_matches:
        suppressed = False
        for accepted in kept:
            if _iou(candidate, accepted) > iou_threshold:
                suppressed = True
                break
        if not suppressed:
            kept.append(candidate)

    return kept


def _iou(a: SymbolMatch, b: SymbolMatch) -> float:
    """Compute intersection-over-union for two SymbolMatch boxes."""
    ax1, ay1, ax2, ay2 = a.x, a.y, a.x + a.width, a.y + a.height
    bx1, by1, bx2, by2 = b.x, b.y, b.x + b.width, b.y + b.height

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)

    inter_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter_area == 0:
        return 0.0

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union_area = area_a + area_b - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


# ---------------------------------------------------------------------------
# Text association
# ---------------------------------------------------------------------------


def find_nearby_text(
    match: SymbolMatch,
    page_text: str,
    radius_px: int = 80,
) -> list[str]:
    """Placeholder: associate P&ID tag strings near a detected symbol.

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
    import re

    tag_pattern = re.compile(
        r"\b[A-Z]{1,4}[-_]?\d{3,5}[A-Z]?\b",
    )
    tags = list(set(tag_pattern.findall(page_text)))
    return tags[:10]  # limit to 10 nearest candidates


# ---------------------------------------------------------------------------
# Annotation
# ---------------------------------------------------------------------------

# Colour palette per symbol (cycles if more symbols than colours)
_COLOURS = [
    (0, 255, 0),    # green
    (255, 128, 0),  # orange
    (0, 128, 255),  # blue
    (255, 0, 255),  # magenta
    (0, 255, 255),  # cyan
    (255, 255, 0),  # yellow
]


def annotate_page_image(
    image: np.ndarray,
    matches: list[SymbolMatch],
    draw_labels: bool = True,
) -> np.ndarray:
    """Draw coloured bounding boxes and labels on a copy of the page image.

    Args:
        image: BGR page image (will not be modified in-place).
        matches: List of detections to annotate.
        draw_labels: Whether to draw symbol name + confidence text.

    Returns:
        Annotated BGR image copy.
    """
    annotated = image.copy()

    # Assign a consistent colour per unique symbol name
    unique_names = list(dict.fromkeys(m.symbol_name for m in matches))
    colour_map = {name: _COLOURS[i % len(_COLOURS)] for i, name in enumerate(unique_names)}

    for m in matches:
        colour = colour_map[m.symbol_name]
        cv2.rectangle(annotated, (m.x, m.y), (m.x + m.width, m.y + m.height), colour, 2)

        if draw_labels:
            label = f"{m.symbol_name} {m.confidence:.2f}"
            label_y = max(m.y - 6, 14)
            cv2.putText(
                annotated, label,
                (m.x, label_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, colour, 1, cv2.LINE_AA,
            )

    return annotated
