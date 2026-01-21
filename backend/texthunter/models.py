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
