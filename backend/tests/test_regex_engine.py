"""Tests for the regex engine module."""

import re

import pytest

from texthunter.regex_engine import extract_matches, guess_regex


class TestExtractMatches:
    """Tests for extract_matches function."""

    def test_basic_extraction(self):
        """Test basic regex matching."""
        text_content = {
            "test.pdf": {
                1: 'Line connects to 10"-FG-001 at valve',
                2: 'Flow from 2"-CWS-505 continues',
            }
        }

        matches = list(
            extract_matches(
                text_content=text_content,
                keyword_regex=r'\d+"-[A-Z]+-\d+',
            )
        )

        assert len(matches) == 2
        assert matches[0].match_found == '10"-FG-001'
        assert matches[0].page == 1
        assert matches[1].match_found == '2"-CWS-505'
        assert matches[1].page == 2

    def test_context_extraction(self):
        """Test that context is extracted around matches."""
        text_content = {"test.pdf": {1: "This is a test 10-ABC-001 with context here"}}

        matches = list(
            extract_matches(
                text_content=text_content,
                keyword_regex=r"\d+-[A-Z]+-\d+",
            )
        )

        assert len(matches) == 1
        assert "10-ABC-001" in matches[0].context
        assert "test" in matches[0].context
        assert "context" in matches[0].context

    def test_file_identifier_extraction(self):
        """Test extraction of metadata from filenames."""
        text_content = {"2024_SiteA_PID-001.pdf": {1: "Contains 10-FG-001 here"}}

        matches = list(
            extract_matches(
                text_content=text_content,
                keyword_regex=r"\d+-[A-Z]+-\d+",
                file_identifier_regex=r"^(\d{4})_([^_]+)",
            )
        )

        assert len(matches) == 1
        assert matches[0].project_id == "2024"
        assert matches[0].sheet_no == "SiteA"

    def test_invalid_regex(self):
        """Test that invalid regex raises ValueError."""
        with pytest.raises(ValueError, match="Invalid keyword regex"):
            list(extract_matches(text_content={}, keyword_regex="[invalid"))


class TestGuessRegex:
    """Tests for guess_regex function."""

    def test_pipe_line_numbers(self):
        """Test guessing pattern for pipe line numbers."""
        examples = ['10"-FG-001', '2"-CWS-505']
        pattern, explanation = guess_regex(examples)

        assert "regex" in explanation.lower()
        # Pattern should be valid regex
        compiled = re.compile(pattern)
        for ex in examples:
            assert compiled.fullmatch(ex), f"Pattern {pattern} did not match {ex}"

    def test_simple_pattern(self):
        """Test guessing pattern for simple strings."""
        examples = ["ABC-001", "DEF-002", "GHI-003"]
        pattern, explanation = guess_regex(examples)

        assert "regex" in explanation.lower()
        # Pattern should be valid regex
        compiled = re.compile(pattern)
        for ex in examples:
            assert compiled.fullmatch(ex), f"Pattern {pattern} did not match {ex}"

    def test_minimum_examples(self):
        """Test that at least 2 examples are required."""
        with pytest.raises(ValueError, match="At least 2 examples"):
            guess_regex(["single"])

    def test_generated_pattern_matches_examples(self):
        """Test that generated pattern matches the input examples."""
        examples = ["TAG-001-A", "TAG-002-B", "TAG-003-C"]
        pattern, _ = guess_regex(examples)

        compiled = re.compile(pattern)
        for ex in examples:
            assert compiled.fullmatch(ex), f"Pattern {pattern} did not match {ex}"
