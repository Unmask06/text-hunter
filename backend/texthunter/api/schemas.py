"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request payload for text extraction."""

    filenames: list[str] = Field(..., description="List of PDF filenames")
    file_identifier_regex: str | None = Field(
        None, description="Regex to extract metadata from filenames"
    )
    keyword_regex: str = Field(..., description="Regex pattern to match in text")
    text_content: dict[str, dict[int, str]] = Field(
        ..., description="Map of filename -> {page_number: text_content}"
    )


class RegexGuessRequest(BaseModel):
    """Request payload for regex generation from examples."""

    examples: list[str] = Field(
        ..., min_length=2, description="Example strings to generate regex from"
    )


class MatchResult(BaseModel):
    """A single match result."""

    source_file: str
    project_id: str | None = None
    sheet_no: str | None = None
    page: int
    match_found: str
    context: str = Field(..., description="±20 chars around the match")


class ExtractionResponse(BaseModel):
    """Response from extraction endpoint."""

    matches: list[MatchResult]
    total_count: int
    preview_count: int = Field(default=10, description="Number of matches in preview")


class RegexGuessResponse(BaseModel):
    """Response from regex guess endpoint."""

    pattern: str = Field(..., description="Generated regex pattern")
    explanation: str = Field(..., description="Explanation of the generated pattern")
    test_results: dict[str, bool] = Field(
        ..., description="Which examples match the generated pattern"
    )


class ExportRequest(BaseModel):
    """Request payload for Excel export."""

    matches: list[MatchResult]
    include_context: bool = Field(default=True)


# ---------------------------------------------------------------------------
# Vision schemas — P&ID symbol detection
# ---------------------------------------------------------------------------


class BoundingBox(BaseModel):
    """Pixel bounding box in image coordinates."""

    x: int
    y: int
    width: int
    height: int


class SymbolTemplate(BaseModel):
    """A named symbol template encoded as a base64 PNG image."""

    name: str = Field(
        ..., description="Human-readable symbol name, e.g. 'Control Valve'"
    )
    image_b64: str = Field(..., description="Base64-encoded PNG of the template image")
    source_legend_page: int | None = Field(
        None, description="Legend page this template was extracted from"
    )


class LegendExtractRequest(BaseModel):
    """Extract symbol templates from a legend PDF page rendered as an image."""

    image_b64: str = Field(..., description="Base64-encoded PNG of the legend page")
    bounding_boxes: list[BoundingBox] | None = Field(
        None,
        description="User-annotated regions. If None, auto-segmentation is attempted.",
    )
    symbol_names: list[str] | None = Field(
        None,
        description=(
            "Names for each bounding_box (required when bounding_boxes is provided)."
        ),
    )


class LegendExtractResponse(BaseModel):
    """Extracted templates from a legend page."""

    templates: list[SymbolTemplate]
    annotated_image_b64: str = Field(
        ..., description="Legend with detected regions highlighted"
    )


class RenderPageRequest(BaseModel):
    """Render a single PDF page to an image."""

    pdf_b64: str = Field(..., description="Base64-encoded PDF bytes")
    page: int = Field(default=1, ge=1, description="1-based page number to render")
    dpi: int = Field(default=150, ge=72, le=300, description="Rendering resolution")


class RenderPageResponse(BaseModel):
    """Rendered page image."""

    image_b64: str
    page: int
    width: int
    height: int
    total_pages: int


class SymbolDetectRequest(BaseModel):
    """Detect symbols across pages of a target P&ID PDF."""

    pdf_b64: str = Field(..., description="Base64-encoded PDF file to scan")
    templates: list[SymbolTemplate] = Field(
        ..., description="Symbol templates to search for"
    )
    dpi: int = Field(default=150, ge=72, le=300, description="PDF rendering resolution")
    threshold: float = Field(
        default=0.75, ge=0.5, le=0.99, description="Confidence threshold"
    )
    scale_range: tuple[float, float] = Field(default=(0.7, 1.3))
    enable_rotation: bool = Field(
        default=False, description="Search rotated variants (4× slower)"
    )
    nearby_text_radius_px: int = Field(default=80)
    existing_text_content: dict[str, dict[int, str]] | None = Field(
        None,
        description=(
            "Pre-extracted text from the PDF worker (filename -> page -> text). "
            "Used for tag association; skips re-extraction when provided."
        ),
    )


class SymbolDetectionResult(BaseModel):
    """A single symbol detection hit."""

    symbol_name: str
    page: int
    bbox: BoundingBox
    confidence: float
    associated_tags: list[str] = Field(default_factory=list)
    scale: float = Field(default=1.0)
    angle_deg: float = Field(default=0.0)


class SymbolDetectResponse(BaseModel):
    """All detections across the entire P&ID PDF."""

    results: list[SymbolDetectionResult]
    total_count: int
    pages_processed: int
    annotated_pages_b64: list[str] = Field(
        default_factory=list,
        description="Base64 PNG of each processed page with bounding boxes drawn",
    )


class VisionExportRequest(BaseModel):
    """Export symbol detection results to Excel."""

    results: list[SymbolDetectionResult]
    include_annotated_images: bool = Field(default=False)
