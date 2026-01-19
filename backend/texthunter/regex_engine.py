"""Core regex processing logic for text extraction and pattern generation."""

import logging
import re
from collections.abc import Iterator

from .models import MatchResult

logger = logging.getLogger(__name__)


def extract_matches(
    text_content: dict[str, dict[int, str]],
    keyword_regex: str,
    file_identifier_regex: str | None = None,
    context_chars: int = 20,
) -> Iterator[MatchResult]:
    """
    Apply keyword regex to text content and yield match results.

    Args:
        text_content: Map of filename -> {page_number: text_content}
        keyword_regex: Regex pattern to find matches
        file_identifier_regex: Optional regex to extract metadata from filenames
        context_chars: Number of characters to include around match

    Yields:
        MatchResult objects for each match found
    """
    logger.debug("Compiling keyword regex: %s", keyword_regex)
    try:
        pattern = re.compile(keyword_regex)
    except re.error as e:
        logger.error("Invalid keyword regex: %s", e)
        raise ValueError(f"Invalid keyword regex: {e}") from e

    file_pattern = None
    if file_identifier_regex:
        logger.debug("Compiling file identifier regex: %s", file_identifier_regex)
        try:
            file_pattern = re.compile(file_identifier_regex)
        except re.error as e:
            logger.error("Invalid file identifier regex: %s", e)
            raise ValueError(f"Invalid file identifier regex: {e}") from e

    total_matches = 0
    for filename, pages in text_content.items():
        logger.debug("Processing file: %s (%d pages)", filename, len(pages))

        # Extract file metadata if pattern provided
        project_id = None
        sheet_no = None
        if file_pattern:
            file_match = file_pattern.search(filename)
            if file_match:
                groups = file_match.groups()
                if len(groups) >= 1:
                    project_id = groups[0]
                if len(groups) >= 2:
                    sheet_no = groups[1]
                logger.debug(
                    "File metadata extracted: project_id=%s, sheet_no=%s",
                    project_id,
                    sheet_no,
                )

        # Search each page
        for page_num, text in pages.items():
            page_matches = 0
            for match in pattern.finditer(text):
                # Extract context around match
                start = max(0, match.start() - context_chars)
                end = min(len(text), match.end() + context_chars)
                context = text[start:end]

                # Add ellipsis if truncated
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."

                page_matches += 1
                total_matches += 1

                yield MatchResult(
                    source_file=filename,
                    project_id=project_id,
                    sheet_no=sheet_no,
                    page=int(page_num),
                    match_found=match.group(),
                    context=context,
                )

            if page_matches > 0:
                logger.debug("Page %d: found %d matches", page_num, page_matches)

    logger.info("Total matches found: %d", total_matches)


def guess_regex(examples: list[str]) -> tuple[str, str]:
    """
    Generate a regex pattern from example strings using token-replacement algorithm.

    Args:
        examples: List of example strings (minimum 2)

    Returns:
        Tuple of (pattern, explanation)
    """
    logger.debug("Generating regex from %d examples", len(examples))

    if len(examples) < 2:
        raise ValueError("At least 2 examples required")

    # Tokenize each example
    tokenized = [_tokenize(ex) for ex in examples]
    logger.debug("Tokenized examples: %s", tokenized)

    # Find common structure
    if not all(len(t) == len(tokenized[0]) for t in tokenized):
        logger.debug("Token counts differ, using simple pattern builder")
        # Different token counts - try simpler approach
        pattern = _build_simple_pattern(examples)
        return pattern, "Generated pattern based on character classes"

    # Build pattern from common tokens
    pattern_parts = []
    explanations = []

    for i, token in enumerate(tokenized[0]):
        token_type = token[0]
        # Check if all examples have same token type at this position
        all_same_type = all(t[i][0] == token_type for t in tokenized)

        if all_same_type:
            if token_type == "digits":
                pattern_parts.append(r"\d+")
                explanations.append("digits")
            elif token_type == "letters_upper":
                pattern_parts.append(r"[A-Z]+")
                explanations.append("uppercase letters")
            elif token_type == "letters_lower":
                pattern_parts.append(r"[a-z]+")
                explanations.append("lowercase letters")
            elif token_type == "letters_mixed":
                pattern_parts.append(r"[A-Za-z]+")
                explanations.append("letters")
            elif token_type == "separator":
                # Check if all separators are the same
                all_same_sep = all(t[i][1] == token[1] for t in tokenized)
                if all_same_sep:
                    pattern_parts.append(re.escape(token[1]))
                    explanations.append(f"'{token[1]}'")
                else:
                    pattern_parts.append(r"[-_./\\]")
                    explanations.append("separator")
            elif token_type == "special":
                # Literal special char (like ")
                all_same = all(t[i][1] == token[1] for t in tokenized)
                if all_same:
                    pattern_parts.append(re.escape(token[1]))
                    explanations.append(f"'{token[1]}'")
                else:
                    pattern_parts.append(r".")
                    explanations.append("any character")
        else:
            pattern_parts.append(r".+?")
            explanations.append("any text")

    pattern = "".join(pattern_parts)
    explanation = " + ".join(explanations)

    logger.info("Generated pattern: %s", pattern)

    return pattern, f"Pattern structure: {explanation}"


def _tokenize(text: str) -> list[tuple[str, str]]:
    """
    Break text into typed tokens.

    Returns list of (token_type, token_value) tuples.
    """
    tokens = []
    current_type = None
    current_value = ""

    for char in text:
        if char.isdigit():
            char_type = "digits"
        elif char.isupper():
            char_type = "letters_upper"
        elif char.islower():
            char_type = "letters_lower"
        elif char in "-_./\\":
            char_type = "separator"
        else:
            char_type = "special"

        if char_type == current_type or (
            current_type in ("letters_upper", "letters_lower", "letters_mixed")
            and char_type in ("letters_upper", "letters_lower")
        ):
            current_value += char
            if (
                current_type in ("letters_upper", "letters_lower")
                and char_type != current_type
            ):
                current_type = "letters_mixed"
        else:
            if current_value:
                tokens.append((current_type, current_value))
            current_type = char_type
            current_value = char

    if current_value:
        tokens.append((current_type, current_value))

    return tokens


def _build_simple_pattern(examples: list[str]) -> str:
    """Build a simple pattern when token counts differ."""
    # Find common prefix and suffix
    prefix = _common_prefix(examples)
    suffix = _common_suffix(examples)

    if prefix or suffix:
        middle = r".+"
        return re.escape(prefix) + middle + re.escape(suffix)

    # Fallback: character class based pattern
    has_digits = any(any(c.isdigit() for c in ex) for ex in examples)
    has_upper = any(any(c.isupper() for c in ex) for ex in examples)
    has_dash = any("-" in ex for ex in examples)

    parts = []
    if has_digits:
        parts.append(r"\d+")
    if has_dash:
        parts.append(r"-")
    if has_upper:
        parts.append(r"[A-Z]+")
    if has_dash and has_digits:
        parts.append(r"-\d+")

    return "".join(parts) if parts else r".+"


def _common_prefix(strings: list[str]) -> str:
    """Find common prefix among strings."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def _common_suffix(strings: list[str]) -> str:
    """Find common suffix among strings."""
    if not strings:
        return ""
    suffix = strings[0]
    for s in strings[1:]:
        while not s.endswith(suffix):
            suffix = suffix[1:]
            if not suffix:
                return ""
    return suffix
