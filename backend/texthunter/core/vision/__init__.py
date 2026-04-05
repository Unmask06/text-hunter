"""P&ID symbol detection and image processing utilities."""

from .opencv import (
    SymbolMatch,
    annotate_page_image,
    auto_segment_legend_grid,
    base64_to_image,
    detect_symbol_in_page,
    extract_legend_templates,
    image_to_base64_png,
    pil_to_numpy,
    suppress_overlapping_matches,
)
from .operations import (
    find_nearby_text,
    render_pdf_pages,
)

__all__ = [
    "SymbolMatch",
    "annotate_page_image",
    "auto_segment_legend_grid",
    "base64_to_image",
    "detect_symbol_in_page",
    "extract_legend_templates",
    "find_nearby_text",
    "image_to_base64_png",
    "pil_to_numpy",
    "render_pdf_pages",
    "suppress_overlapping_matches",
]
