"""Tests for pattern constants."""


from gitco.patterns.constants import (
    API_PATTERNS,
    BREAKING_CHANGE_PATTERNS,
    CONFIGURATION_PATTERNS,
    DATABASE_PATTERNS,
    DEPENDENCY_PATTERNS,
    DEPRECATION_PATTERNS,
    SECURITY_PATTERNS,
    get_all_patterns,
    get_patterns_for_type,
)


class TestPatternConstants:
    """Test pattern constants."""

    def test_breaking_change_patterns_exist(self) -> None:
        """Test that breaking change patterns are defined."""
        assert BREAKING_CHANGE_PATTERNS is not None
        assert isinstance(BREAKING_CHANGE_PATTERNS, dict)
        assert len(BREAKING_CHANGE_PATTERNS) > 0
        # Check that all values are lists
        for patterns in BREAKING_CHANGE_PATTERNS.values():
            assert isinstance(patterns, list)
            assert len(patterns) > 0

    def test_deprecation_patterns_exist(self) -> None:
        """Test that deprecation patterns are defined."""
        assert DEPRECATION_PATTERNS is not None
        assert isinstance(DEPRECATION_PATTERNS, dict)
        assert len(DEPRECATION_PATTERNS) > 0
        # Check that all values are lists
        for patterns in DEPRECATION_PATTERNS.values():
            assert isinstance(patterns, list)
            assert len(patterns) > 0

    def test_security_patterns_exist(self) -> None:
        """Test that security patterns are defined."""
        assert SECURITY_PATTERNS is not None
        assert isinstance(SECURITY_PATTERNS, dict)
        assert len(SECURITY_PATTERNS) > 0
        # Check that all values are lists
        for patterns in SECURITY_PATTERNS.values():
            assert isinstance(patterns, list)
            assert len(patterns) > 0

    def test_api_patterns_exist(self) -> None:
        """Test that API patterns are defined."""
        assert API_PATTERNS is not None
        assert isinstance(API_PATTERNS, list)
        assert len(API_PATTERNS) > 0

    def test_configuration_patterns_exist(self) -> None:
        """Test that configuration patterns are defined."""
        assert CONFIGURATION_PATTERNS is not None
        assert isinstance(CONFIGURATION_PATTERNS, list)
        assert len(CONFIGURATION_PATTERNS) > 0

    def test_database_patterns_exist(self) -> None:
        """Test that database patterns are defined."""
        assert DATABASE_PATTERNS is not None
        assert isinstance(DATABASE_PATTERNS, list)
        assert len(DATABASE_PATTERNS) > 0

    def test_dependency_patterns_exist(self) -> None:
        """Test that dependency patterns are defined."""
        assert DEPENDENCY_PATTERNS is not None
        assert isinstance(DEPENDENCY_PATTERNS, list)
        assert len(DEPENDENCY_PATTERNS) > 0

    def test_get_patterns_for_type_valid(self) -> None:
        """Test get_patterns_for_type with valid type."""
        patterns = get_patterns_for_type("breaking_change")
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_get_patterns_for_type_invalid(self) -> None:
        """Test get_patterns_for_type with invalid type."""
        patterns = get_patterns_for_type("invalid_type")
        assert patterns == []

    def test_get_patterns_for_type_none(self) -> None:
        """Test get_patterns_for_type with None type."""
        patterns = get_patterns_for_type("")
        assert patterns == []

    def test_get_all_patterns(self) -> None:
        """Test get_all_patterns function."""
        all_patterns = get_all_patterns()
        assert isinstance(all_patterns, dict)
        assert "breaking_change" in all_patterns
        assert "deprecation" in all_patterns
        assert "security" in all_patterns

    def test_pattern_structure(self) -> None:
        """Test that patterns have the expected structure."""
        # Test dictionary-based patterns
        for pattern_dict in [
            BREAKING_CHANGE_PATTERNS,
            DEPRECATION_PATTERNS,
            SECURITY_PATTERNS,
        ]:
            for patterns in pattern_dict.values():
                for pattern in patterns:
                    assert isinstance(pattern, str)
                    assert len(pattern) > 0

        # Test list-based patterns
        for pattern_list in [
            API_PATTERNS,
            CONFIGURATION_PATTERNS,
            DATABASE_PATTERNS,
            DEPENDENCY_PATTERNS,
        ]:
            for pattern in pattern_list:
                assert isinstance(pattern, str)
                assert len(pattern) > 0

    def test_pattern_uniqueness(self) -> None:
        """Test that patterns are unique within each category."""
        # Test dictionary-based patterns
        for pattern_dict in [
            BREAKING_CHANGE_PATTERNS,
            DEPRECATION_PATTERNS,
            SECURITY_PATTERNS,
        ]:
            all_patterns = []
            for patterns in pattern_dict.values():
                all_patterns.extend(patterns)
            unique_patterns = set(all_patterns)
            assert len(unique_patterns) == len(all_patterns)

        # Test list-based patterns
        for pattern_list in [
            API_PATTERNS,
            CONFIGURATION_PATTERNS,
            DATABASE_PATTERNS,
            DEPENDENCY_PATTERNS,
        ]:
            unique_patterns = set(pattern_list)
            assert len(unique_patterns) == len(pattern_list)

    def test_pattern_content_quality(self) -> None:
        """Test that patterns contain meaningful content."""
        # Test dictionary-based patterns
        for pattern_dict in [
            BREAKING_CHANGE_PATTERNS,
            DEPRECATION_PATTERNS,
            SECURITY_PATTERNS,
        ]:
            for patterns in pattern_dict.values():
                for pattern in patterns:
                    # Patterns should not be empty or just whitespace
                    assert pattern.strip() != ""
                    # Patterns should contain some regex-like content or be meaningful strings
                    has_regex_chars = any(
                        char in pattern
                        for char in ["*", "+", "?", "\\", "[", "]", "(", ")", "|"]
                    )
                    has_meaningful_content = len(pattern.strip()) >= 2
                    assert (
                        has_regex_chars or has_meaningful_content
                    ), f"Pattern '{pattern}' lacks regex chars or meaningful content"

        # Test list-based patterns
        for pattern_list in [
            API_PATTERNS,
            CONFIGURATION_PATTERNS,
            DATABASE_PATTERNS,
            DEPENDENCY_PATTERNS,
        ]:
            for pattern in pattern_list:
                # Patterns should not be empty or just whitespace
                assert pattern.strip() != ""
                # Patterns should contain some regex-like content or be meaningful strings
                has_regex_chars = any(
                    char in pattern
                    for char in ["*", "+", "?", "\\", "[", "]", "(", ")", "|"]
                )
                has_meaningful_content = len(pattern.strip()) >= 2
                assert (
                    has_regex_chars or has_meaningful_content
                ), f"Pattern '{pattern}' lacks regex chars or meaningful content"

    def test_pattern_categories_coverage(self) -> None:
        """Test that all pattern categories are covered."""
        all_patterns = get_all_patterns()
        expected_categories = [
            "breaking_change",
            "deprecation",
            "security",
            "api",
            "configuration",
            "database",
            "dependency",
        ]

        for category in expected_categories:
            assert category in all_patterns
            assert isinstance(all_patterns[category], list)
            assert len(all_patterns[category]) > 0

    def test_pattern_function_integration(self) -> None:
        """Test integration between pattern functions."""
        # Test that get_patterns_for_type returns the same as get_all_patterns for each type
        all_patterns = get_all_patterns()

        for pattern_type in all_patterns.keys():
            specific_patterns = get_patterns_for_type(pattern_type)
            assert specific_patterns == all_patterns[pattern_type]
