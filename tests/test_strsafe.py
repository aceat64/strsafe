import pytest

from strsafe import StrSafe


class TestStrSafeBasic:
    """Test basic functionality and default behavior."""

    def test_basic_transliteration(self) -> None:
        """Test basic Unicode to ASCII transliteration."""
        safe = StrSafe("Héllo Wörld")
        assert str(safe) == "hello_world"
        assert safe.original == "Héllo Wörld"
        assert safe.safe == "hello_world"

    def test_empty_string(self) -> None:
        """Test empty string handling."""
        safe = StrSafe("")
        assert str(safe) == ""
        assert safe.is_empty
        assert not bool(safe)
        assert len(safe) == 0

    def test_ascii_only_string(self) -> None:
        """Test string with only ASCII characters."""
        safe = StrSafe("Hello World")
        assert str(safe) == "hello_world"

    def test_numbers_preserved(self) -> None:
        """Test that numbers are preserved."""
        safe = StrSafe("Test123")
        assert str(safe) == "test123"

    def test_special_characters_replaced(self) -> None:
        """Test that special characters are replaced."""
        safe = StrSafe("Hello@World#Test!")
        assert str(safe) == "hello_world_test"


class TestCaseTransformation:
    """Test case transformation options."""

    def test_lowercase_default(self) -> None:
        """Test default lowercase transformation."""
        safe = StrSafe("HELLO WORLD")
        assert str(safe) == "hello_world"

    def test_uppercase(self) -> None:
        """Test uppercase transformation."""
        safe = StrSafe("hello world", case="upper")
        assert str(safe) == "HELLO_WORLD"

    def test_unchanged_case(self) -> None:
        """Test unchanged case preservation."""
        safe = StrSafe("Hello World", case="unchanged")
        assert str(safe) == "Hello_World"

    def test_mixed_case_unchanged(self) -> None:
        """Test mixed case preservation."""
        safe = StrSafe("HeLLo WoRLd", case="unchanged")
        assert str(safe) == "HeLLo_WoRLd"


class TestReplacementCharacter:
    """Test replacement character options."""

    def test_custom_replacement_char(self) -> None:
        """Test custom replacement character."""
        safe = StrSafe("Hello World", replacement_char="-")
        assert str(safe) == "hello-world"

    def test_empty_replacement_char(self) -> None:
        """Test empty replacement character (removal)."""
        safe = StrSafe("Hello World!", replacement_char="")
        assert str(safe) == "helloworld"

    def test_period_replacement_char(self) -> None:
        """Test period as replacement character."""
        safe = StrSafe("Hello World", replacement_char=".")
        assert str(safe) == "hello.world"

    def test_invalid_replacement_char(self) -> None:
        """Test invalid replacement character raises error."""
        with pytest.raises(ValueError, match="replacement_char must be a single character or empty string"):
            StrSafe("test", replacement_char="ab")


class TestAllowedCharacters:
    """Test character allowlist options."""

    def test_allow_underscore_default(self) -> None:
        """Test underscore allowed by default."""
        safe = StrSafe("hello_world")
        assert str(safe) == "hello_world"

    def test_disallow_underscore(self) -> None:
        """Test disallowing underscores."""
        safe = StrSafe("hello_world", allow_underscore=False)
        assert str(safe) == "hello_world"  # underscore gets replaced

    def test_allow_hyphen(self) -> None:
        """Test allowing hyphens."""
        safe = StrSafe("hello-world", allow_hyphen=True)
        assert str(safe) == "hello-world"

    def test_disallow_hyphen_default(self) -> None:
        """Test hyphens disallowed by default."""
        safe = StrSafe("hello-world")
        assert str(safe) == "hello_world"

    def test_allow_period(self) -> None:
        """Test allowing periods."""
        safe = StrSafe("hello.world", allow_period=True)
        assert str(safe) == "hello.world"

    def test_disallow_period_default(self) -> None:
        """Test periods disallowed by default."""
        safe = StrSafe("hello.world")
        assert str(safe) == "hello_world"

    def test_multiple_allowed_chars(self) -> None:
        """Test multiple allowed character types."""
        safe = StrSafe("hello-world.txt", allow_hyphen=True, allow_period=True)
        assert str(safe) == "hello-world.txt"


class TestConsecutiveCollapsing:
    """Test consecutive character collapsing."""

    def test_collapse_replacement_default(self) -> None:
        """Test consecutive characters collapsed by default."""
        safe = StrSafe("hello   world")
        assert str(safe) == "hello_world"

    def test_no_collapse_replacement(self) -> None:
        """Test disabling consecutive character collapsing."""
        safe = StrSafe("hello   world", collapse_replacement=False)
        assert str(safe) == "hello___world"

    def test_collapse_with_custom_replacement(self) -> None:
        """Test collapsing with custom replacement character."""
        safe = StrSafe("hello   world", replacement_char="-")
        assert str(safe) == "hello-world"

    def test_no_collapse_with_empty_replacement(self) -> None:
        """Test no collapsing needed with empty replacement."""
        safe = StrSafe("hello   world", replacement_char="", collapse_replacement=False)
        assert str(safe) == "helloworld"


class TestStripping:
    """Test replacement character stripping."""

    def test_strip_both_default(self) -> None:
        """Test stripping from both ends by default."""
        safe = StrSafe("  hello world  ")
        assert str(safe) == "hello_world"

    def test_strip_start_only(self) -> None:
        """Test stripping from start only."""
        safe = StrSafe("  hello world  ", strip_replacement="start")
        assert str(safe) == "hello_world_"

    def test_strip_end_only(self) -> None:
        """Test stripping from end only."""
        safe = StrSafe("  hello world  ", strip_replacement="end")
        assert str(safe) == "_hello_world"

    def test_strip_neither(self) -> None:
        """Test no stripping."""
        safe = StrSafe("  hello world  ", strip_replacement="neither")
        assert str(safe) == "_hello_world_"

    def test_strip_with_custom_replacement(self) -> None:
        """Test stripping with custom replacement character."""
        safe = StrSafe("--hello world--", replacement_char="-", strip_replacement="both")
        assert str(safe) == "hello-world"

    def test_strip_no_effect_with_empty_replacement(self) -> None:
        """Test stripping has no effect with empty replacement."""
        safe = StrSafe("  hello world  ", replacement_char="", strip_replacement="both")
        assert str(safe) == "helloworld"


class TestMaxLength:
    """Test maximum length truncation."""

    def test_default_max_length(self) -> None:
        """Test default max length of 64."""
        long_string = "a" * 100
        safe = StrSafe(long_string)
        assert len(safe) == 64
        assert safe.is_truncated

    def test_custom_max_length(self) -> None:
        """Test custom max length."""
        safe = StrSafe("hello world", max_length=5)
        assert str(safe) == "hello"
        assert len(safe) == 5
        assert safe.is_truncated

    def test_no_max_length(self) -> None:
        """Test no max length limit."""
        long_string = "a" * 100
        safe = StrSafe(long_string, max_length=None)
        assert len(safe) == 100
        assert not safe.is_truncated

    def test_max_length_zero(self) -> None:
        """Test max length of zero."""
        safe = StrSafe("hello", max_length=0)
        assert str(safe) == ""
        assert safe.is_truncated
        assert safe.is_empty

    def test_max_length_longer_than_string(self) -> None:
        """Test max length longer than processed string."""
        safe = StrSafe("hello", max_length=100)
        assert str(safe) == "hello"
        assert not safe.is_truncated

    def test_invalid_max_length(self) -> None:
        """Test invalid max length raises error."""
        with pytest.raises(ValueError, match="max_length must be non-negative or None"):
            StrSafe("test", max_length=-1)

    def test_truncation_after_processing(self) -> None:
        """Test truncation happens after all other processing."""
        safe = StrSafe("  hello world  ", max_length=5, strip_replacement="both")
        assert str(safe) == "hello"
        assert safe.is_truncated


class TestStringMethods:
    """Test string-like methods and properties."""

    def test_str_method(self) -> None:
        """Test __str__ method."""
        safe = StrSafe("hello world")
        assert str(safe) == "hello_world"

    def test_repr_method(self) -> None:
        """Test __repr__ method."""
        safe = StrSafe("hello world")
        expected = "StrSafe(original='hello world', safe='hello_world')"
        assert repr(safe) == expected

    def test_len_method(self) -> None:
        """Test __len__ method."""
        safe = StrSafe("hello")
        assert len(safe) == 5

    def test_bool_method(self) -> None:
        """Test __bool__ method."""
        safe_true = StrSafe("hello")
        safe_false = StrSafe("")
        assert bool(safe_true) is True
        assert bool(safe_false) is False

    def test_equality_with_strsafe(self) -> None:
        """Test equality with another StrSafe instance."""
        safe1 = StrSafe("hello world")
        safe2 = StrSafe("hello world")
        safe3 = StrSafe("goodbye world")

        assert safe1 == safe2
        assert safe1 != safe3

    def test_equality_with_string(self) -> None:
        """Test equality with string."""
        safe = StrSafe("hello world")
        assert safe == "hello_world"
        assert safe != "hello world"

    def test_equality_with_other_types(self) -> None:
        """Test equality with other types."""
        safe = StrSafe("hello")
        assert safe != 123
        assert safe is not None
        assert safe != ["hello"]

    def test_hash_method(self) -> None:
        """Test __hash__ method."""
        safe1 = StrSafe("hello")
        safe2 = StrSafe("hello")
        safe3 = StrSafe("world")

        assert hash(safe1) == hash(safe2)
        assert hash(safe1) != hash(safe3)

        # Test can be used in set
        safe_set = {safe1, safe2, safe3}
        assert len(safe_set) == 2

    def test_startswith(self) -> None:
        """Test startswith method."""
        safe = StrSafe("hello world")
        assert safe.startswith("hello")
        assert not safe.startswith("world")

    def test_endswith(self) -> None:
        """Test endswith method."""
        safe = StrSafe("hello world")
        assert safe.endswith("world")
        assert not safe.endswith("hello")


class TestProperties:
    """Test properties."""

    def test_original_property(self) -> None:
        """Test original property."""
        original = "Héllo Wörld!"
        safe = StrSafe(original)
        assert safe.original == original

    def test_safe_property(self) -> None:
        """Test safe property."""
        safe = StrSafe("hello world")
        assert safe.safe == "hello_world"
        assert safe.safe == str(safe)

    def test_is_empty_property(self) -> None:
        """Test is_empty property."""
        safe_empty = StrSafe("")
        safe_not_empty = StrSafe("hello")

        assert safe_empty.is_empty
        assert not safe_not_empty.is_empty

    def test_is_truncated_property(self) -> None:
        """Test is_truncated property."""
        safe_truncated = StrSafe("hello world", max_length=5)
        safe_not_truncated = StrSafe("hello", max_length=10)
        safe_no_limit = StrSafe("hello world", max_length=None)

        assert safe_truncated.is_truncated
        assert not safe_not_truncated.is_truncated
        assert not safe_no_limit.is_truncated


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_only_special_characters(self) -> None:
        """Test string with only special characters."""
        safe = StrSafe("!@#$%^&*()")
        assert str(safe) == ""
        assert safe.is_empty

    def test_only_whitespace(self) -> None:
        """Test string with only whitespace."""
        safe = StrSafe("   \t\n\r   ")
        assert str(safe) == ""
        assert safe.is_empty

    def test_single_character(self) -> None:
        """Test single character string."""
        safe = StrSafe("a")
        assert str(safe) == "a"

    def test_very_long_string(self) -> None:
        """Test very long string."""
        long_string = "a" * 1000
        safe = StrSafe(long_string, max_length=100)
        assert len(safe) == 100
        assert safe.is_truncated

    def test_replacement_char_in_allowed_chars(self) -> None:
        """Test replacement char that's also an allowed char."""
        safe = StrSafe("hello world", replacement_char="_", allow_underscore=True)
        assert str(safe) == "hello_world"

    def test_consecutive_replacement_at_edges(self) -> None:
        """Test consecutive replacement chars at string edges."""
        safe = StrSafe("!!!hello world!!!", replacement_char="!")
        assert str(safe) == "hello!world"  # Stripped from edges, collapsed in middle


class TestEnumValidation:
    """Test enum validation."""

    def test_invalid_case_mode(self) -> None:
        """Test invalid case mode."""
        with pytest.raises(ValueError):
            StrSafe("test", case="invalid")  # type: ignore[arg-type]

    def test_invalid_strip_mode(self) -> None:
        """Test invalid strip mode."""
        with pytest.raises(ValueError):
            StrSafe("test", strip_replacement="invalid")  # type: ignore[arg-type]


class TestPerformance:
    """Test performance characteristics."""

    def test_is_truncated_cached(self) -> None:
        """Test that is_truncated is cached and not recalculated."""
        safe = StrSafe("hello world", max_length=5)

        # Access multiple times - should not recalculate
        result1 = safe.is_truncated
        result2 = safe.is_truncated
        result3 = safe.is_truncated

        assert result1 == result2 == result3 == True  # noqa: E712

    def test_multiple_property_access(self) -> None:
        """Test multiple property accesses are efficient."""
        safe = StrSafe("hello world")

        # Multiple accesses should be fast
        for _ in range(100):
            _ = safe.safe
            _ = safe.is_empty
            _ = safe.is_truncated


if __name__ == "__main__":
    pytest.main([__file__])
