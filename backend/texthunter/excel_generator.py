"""Excel generation utilities using Pandas and Openpyxl."""

from io import BytesIO

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from texthunter.models import MatchResult


def build_dataframe(
    matches: list[MatchResult], include_context: bool = True
) -> pd.DataFrame:
    """Create a DataFrame from match results.

    Args:
        matches: List of MatchResult objects
        include_context: Whether to include the context column

    Returns:
        Pandas DataFrame with match data
    """
    data = []
    for match in matches:
        row = {
            "Source File": match.source_file,
            "Project ID": match.project_id or "",
            "Sheet No": match.sheet_no or "",
            "Page": match.page,
            "Match Found": match.match_found,
        }
        if include_context:
            row["Context (± 20 chars)"] = match.context
        data.append(row)

    return pd.DataFrame(data)


def generate_excel(matches: list[MatchResult], include_context: bool = True) -> BytesIO:
    """Generate an Excel file from match results.

    Args:
        matches: List of MatchResult objects
        include_context: Whether to include the context column

    Returns:
        BytesIO buffer containing the Excel file
    """
    df = build_dataframe(matches, include_context)

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extraction Results")

        # Get the workbook and worksheet for styling
        workbook = writer.book
        worksheet = writer.sheets["Extraction Results"]

        # Style the header row
        header_fill = PatternFill(
            start_color="1F4E79", end_color="1F4E79", fill_type="solid"
        )
        header_font = Font(color="FFFFFF", bold=True)

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except (TypeError, AttributeError):
                    pass

            # Cap width and add padding
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Freeze the header row
        worksheet.freeze_panes = "A2"

    buffer.seek(0)
    return buffer
