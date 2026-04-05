"""API route definitions."""

import logging
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from texthunter.api.configs import configs_router
from texthunter.api.schemas import (
    BoundingBox,
    ExportRequest,
    ExtractionRequest,
    ExtractionResponse,
    LegendExtractRequest,
    LegendExtractResponse,
    RegexGuessRequest,
    RegexGuessResponse,
    RenderPageRequest,
    RenderPageResponse,
    SymbolDetectionResult,
    SymbolDetectRequest,
    SymbolDetectResponse,
    SymbolTemplate,
    VisionExportRequest,
)
from texthunter.core.excel import generate_excel, generate_vision_excel
from texthunter.core.regex import extract_matches, guess_regex
from texthunter.core.vision import (
    annotate_page_image,
    auto_segment_legend_grid,
    base64_to_image,
    detect_symbol_in_page,
    extract_legend_templates,
    find_nearby_text,
    image_to_base64_png,
    render_pdf_pages,
)

logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(configs_router, prefix="/v1/history")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.post("/extract", response_model=ExtractionResponse)
async def extract_data(payload: ExtractionRequest):
    """Run regex extraction on provided text content.

    Returns a preview of the first 10 matches.
    """
    logger.info(
        "Extract request received: %d files, pattern='%s'",
        len(payload.filenames),
        payload.keyword_regex,
    )
    logger.debug("File identifier regex: %s", payload.file_identifier_regex)

    try:
        matches = list(
            extract_matches(
                text_content=payload.text_content,
                keyword_regex=payload.keyword_regex,
                file_identifier_regex=payload.file_identifier_regex,
            )
        )

        logger.info("Extraction complete: %d matches found", len(matches))

        return ExtractionResponse(
            matches=matches[:10],
            total_count=len(matches),
            preview_count=min(10, len(matches)),
        )
    except ValueError as e:
        logger.error("Extraction failed: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/extract-all")
async def extract_all_data(payload: ExtractionRequest):
    """Run regex extraction and return all matches.

    Use this endpoint when preparing for export.
    """
    logger.info(
        "Extract-all request received: %d files, pattern='%s'",
        len(payload.filenames),
        payload.keyword_regex,
    )

    try:
        matches = list(
            extract_matches(
                text_content=payload.text_content,
                keyword_regex=payload.keyword_regex,
                file_identifier_regex=payload.file_identifier_regex,
            )
        )

        logger.info("Full extraction complete: %d matches", len(matches))

        return {
            "matches": [m.model_dump() for m in matches],
            "total_count": len(matches),
        }
    except ValueError as e:
        logger.error("Extraction failed: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/guess-regex", response_model=RegexGuessResponse)
async def generate_regex(payload: RegexGuessRequest):
    """Generate a regex pattern from example strings.

    Requires at least 2 examples.
    """
    logger.info("Regex guess request: %d examples", len(payload.examples))
    logger.debug("Examples: %s", payload.examples)

    try:
        pattern, explanation = guess_regex(payload.examples)

        # Test the pattern against examples
        compiled = re.compile(pattern)
        test_results = {ex: bool(compiled.search(ex)) for ex in payload.examples}

        logger.info("Generated pattern: %s", pattern)
        logger.debug("Test results: %s", test_results)

        return RegexGuessResponse(
            pattern=pattern,
            explanation=explanation,
            test_results=test_results,
        )
    except ValueError as e:
        logger.error("Regex generation failed: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/export")
async def export_excel(payload: ExportRequest):
    """Generate and stream an Excel file from match results."""
    logger.info("Export request: %d matches", len(payload.matches))

    if not payload.matches:
        logger.warning("Export requested with no matches")
        raise HTTPException(status_code=400, detail="No matches to export")

    buffer = generate_excel(payload.matches, payload.include_context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extraction_results_{timestamp}.xlsx"

    logger.info("Excel file generated: %s", filename)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Vision endpoints — P&ID symbol detection
# ---------------------------------------------------------------------------


@router.post("/vision/render-page", response_model=RenderPageResponse)
async def render_pdf_page(payload: RenderPageRequest):
    """Render a single PDF page to a base64 PNG.

    Used by the frontend legend annotation canvas.
    """
    logger.info("Vision render-page: page=%d dpi=%d", payload.page, payload.dpi)

    try:
        pdf_bytes = __import__("base64").b64decode(payload.pdf_b64)
        pages = render_pdf_pages(
            pdf_bytes, dpi=payload.dpi, page_numbers=[payload.page]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF render failed: {e}") from e

    if not pages:
        raise HTTPException(
            status_code=400, detail=f"Page {payload.page} not found in PDF"
        )

    page_no, img = pages[0]
    h, w = img.shape[:2]

    # Determine total page count
    import fitz as _fitz

    with _fitz.open(
        stream=__import__("base64").b64decode(payload.pdf_b64), filetype="pdf"
    ) as doc:
        total = doc.page_count

    return RenderPageResponse(
        image_b64=image_to_base64_png(img),
        page=page_no,
        width=w,
        height=h,
        total_pages=total,
    )


@router.post("/vision/extract-legend", response_model=LegendExtractResponse)
async def extract_legend(payload: LegendExtractRequest):
    """Extract symbol templates from a legend page image.

    If bounding_boxes is provided, crops those regions.
    Otherwise, runs automatic contour-based segmentation.
    """
    logger.info(
        "Vision extract-legend: manual_boxes=%s", payload.bounding_boxes is not None
    )

    try:
        image = base64_to_image(payload.image_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}") from e

    import cv2 as _cv2

    annotated = image.copy()
    templates: list[SymbolTemplate] = []

    if payload.bounding_boxes:
        boxes = [(b.x, b.y, b.width, b.height) for b in payload.bounding_boxes]
        names = payload.symbol_names or [f"Symbol {i + 1}" for i in range(len(boxes))]
        crops = extract_legend_templates(image, boxes)

        for i, (crop, name) in enumerate(zip(crops, names, strict=True)):
            b = payload.bounding_boxes[i]
            _cv2.rectangle(
                annotated, (b.x, b.y), (b.x + b.width, b.y + b.height), (0, 255, 0), 2
            )
            _cv2.putText(
                annotated,
                name,
                (b.x, max(b.y - 4, 14)),
                _cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1,
                _cv2.LINE_AA,
            )
            templates.append(
                SymbolTemplate(name=name, image_b64=image_to_base64_png(crop))
            )
    else:
        segments = auto_segment_legend_grid(image)
        logger.info("Auto-segmented %d candidate symbols", len(segments))

        for i, ((x, y, w, h), crop) in enumerate(segments):
            name = f"Symbol {i + 1}"
            _cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 128, 0), 2)
            _cv2.putText(
                annotated,
                name,
                (x, max(y - 4, 14)),
                _cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 128, 0),
                1,
                _cv2.LINE_AA,
            )
            templates.append(
                SymbolTemplate(name=name, image_b64=image_to_base64_png(crop))
            )

    return LegendExtractResponse(
        templates=templates,
        annotated_image_b64=image_to_base64_png(annotated),
    )


@router.post("/vision/detect-symbols", response_model=SymbolDetectResponse)
async def detect_symbols(payload: SymbolDetectRequest):
    """Detect P&ID symbols across all pages of a target PDF.

    Returns detections with bounding boxes, confidence scores, and nearby tags.
    Annotated page images are included in the response.
    """
    logger.info(
        "Vision detect-symbols: %d templates, dpi=%d, threshold=%.2f",
        len(payload.templates),
        payload.dpi,
        payload.threshold,
    )

    if not payload.templates:
        raise HTTPException(status_code=400, detail="At least one template is required")

    try:
        pdf_bytes = __import__("base64").b64decode(payload.pdf_b64)
        pages = render_pdf_pages(pdf_bytes, dpi=payload.dpi)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF render failed: {e}") from e

    angle_steps = [0.0, 90.0, 180.0, 270.0] if payload.enable_rotation else None

    all_results: list[SymbolDetectionResult] = []
    annotated_pages: list[str] = []

    # Build per-page text lookup from optional pre-extracted content
    page_texts: dict[int, str] = {}
    if payload.existing_text_content:
        for _fname, page_map in payload.existing_text_content.items():
            for page_no_str, text in page_map.items():
                page_no = int(page_no_str)
                page_texts[page_no] = page_texts.get(page_no, "") + "\n" + text

    for page_no, page_img in pages:
        page_matches = []

        for tmpl in payload.templates:
            try:
                template_img = base64_to_image(tmpl.image_b64)
            except Exception:
                logger.warning("Skipping template '%s': invalid image", tmpl.name)
                continue

            matches = detect_symbol_in_page(
                page_image=page_img,
                template=template_img,
                symbol_name=tmpl.name,
                page_number=page_no,
                threshold=payload.threshold,
                scale_range=payload.scale_range,
                angle_steps=angle_steps,
            )
            page_matches.extend(matches)

        # Associate nearby tags if text is available
        text_for_page = page_texts.get(page_no, "")
        for m in page_matches:
            if text_for_page:
                m.associated_tags = find_nearby_text(
                    m, text_for_page, payload.nearby_text_radius_px
                )

            all_results.append(
                SymbolDetectionResult(
                    symbol_name=m.symbol_name,
                    page=m.page,
                    bbox=BoundingBox(x=m.x, y=m.y, width=m.width, height=m.height),
                    confidence=m.confidence,
                    associated_tags=m.associated_tags,
                    scale=m.scale,
                    angle_deg=m.angle_deg,
                )
            )

        annotated = annotate_page_image(page_img, page_matches)
        annotated_pages.append(image_to_base64_png(annotated))

    logger.info(
        "Detection complete: %d hits across %d pages",
        len(all_results),
        len(pages),
    )

    return SymbolDetectResponse(
        results=all_results,
        total_count=len(all_results),
        pages_processed=len(pages),
        annotated_pages_b64=annotated_pages,
    )


@router.post("/vision/export")
async def export_vision_excel(payload: VisionExportRequest):
    """Export symbol detection results to Excel."""
    logger.info("Vision export: %d results", len(payload.results))

    if not payload.results:
        raise HTTPException(status_code=400, detail="No detection results to export")

    buffer = generate_vision_excel(payload.results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"symbol_detection_{timestamp}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
