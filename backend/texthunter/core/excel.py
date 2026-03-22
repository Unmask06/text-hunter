"""Excel generation utilities using Pandas and Openpyxl."""

from io import BytesIO

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from texthunter.api.schemas import MatchResult


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

        # Auto-adjust column widths using pandas (vectorized, avoids cell-by-cell iteration)
        for col_idx, col_name in enumerate(df.columns, start=1):
            header_len = len(str(col_name))
            if len(df) > 0:
                data_max = int(df[col_name].astype(str).str.len().max())
            else:
                data_max = 0
            adjusted_width = min(max(header_len, data_max) + 2, 50)
            worksheet.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

        # Freeze the header row
        worksheet.freeze_panes = "A2"

    buffer.seek(0)
    return buffer

