"""Core business logic exports."""

from texthunter.core.excel import build_dataframe, generate_excel
from texthunter.core.regex import extract_matches, guess_regex

__all__ = ["build_dataframe", "extract_matches", "generate_excel", "guess_regex"]

