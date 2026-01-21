"""API route definitions."""

import logging
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from texthunter.excel_generator import generate_excel
from texthunter.models import (
    ExportRequest,
    ExtractionRequest,
    ExtractionResponse,
    RegexGuessRequest,
    RegexGuessResponse,
)
from texthunter.regex_engine import extract_matches, guess_regex

logger = logging.getLogger(__name__)

router = APIRouter()


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
