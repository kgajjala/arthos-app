"""Tests for ticker validator module."""
import pytest
from app.services.ticker_validator import validate_ticker_format, validate_ticker_list


class TestValidateTickerFormat:
    """Tests for validate_ticker_format function."""
    
    def test_valid_single_letter_ticker(self):
        """Test single letter ticker."""
        assert validate_ticker_format("A") is True
        assert validate_ticker_format("a") is True
    
    def test_valid_standard_tickers(self):
        """Test standard ticker formats."""
        assert validate_ticker_format("AAPL") is True
        assert validate_ticker_format("MSFT") is True
        assert validate_ticker_format("GOOGL") is True
        assert validate_ticker_format("TSLA") is True
    
    def test_valid_ticker_with_dot(self):
        """Test ticker with dot (e.g., BRK.B)."""
        assert validate_ticker_format("BRK.B") is True
        assert validate_ticker_format("BRK.A") is True
    
    def test_valid_numeric_tickers(self):
        """Test numeric tickers."""
        assert validate_ticker_format("123") is True
        assert validate_ticker_format("1") is True
    
    def test_valid_alphanumeric_tickers(self):
        """Test alphanumeric tickers."""
        assert validate_ticker_format("A1") is True
        assert validate_ticker_format("1A") is True
        assert validate_ticker_format("A1B2") is True
    
    def test_invalid_empty_string(self):
        """Test empty string."""
        assert validate_ticker_format("") is False
        assert validate_ticker_format("   ") is False
    
    def test_invalid_too_long(self):
        """Test ticker that's too long."""
        assert validate_ticker_format("ABCDEF") is False  # 6 characters
        assert validate_ticker_format("A" * 10) is False
    
    def test_invalid_special_characters(self):
        """Test tickers with invalid special characters."""
        assert validate_ticker_format("AAPL-") is False
        assert validate_ticker_format("MSFT@") is False
        assert validate_ticker_format("GOOGL#") is False
        assert validate_ticker_format("TSLA$") is False
        assert validate_ticker_format("AAPL MSFT") is False  # Space
    
    def test_invalid_multiple_dots(self):
        """Test ticker with multiple dots."""
        assert validate_ticker_format("BRK.B.C") is False
    
    def test_invalid_dot_at_start_or_end(self):
        """Test ticker with dot at start or end."""
        assert validate_ticker_format(".AAPL") is False
        assert validate_ticker_format("AAPL.") is False


class TestValidateTickerList:
    """Tests for validate_ticker_list function."""
    
    def test_all_valid_tickers(self):
        """Test list with all valid tickers."""
        tickers = ["AAPL", "MSFT", "GOOGL"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["AAPL", "MSFT", "GOOGL"]
        assert invalid == []
    
    def test_all_invalid_tickers(self):
        """Test list with all invalid tickers."""
        tickers = ["INVALID12345", "TOOLONG", "INVALID@"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == []
        assert invalid == ["INVALID12345", "TOOLONG", "INVALID@"]
    
    def test_mixed_valid_invalid_tickers(self):
        """Test list with mixed valid and invalid tickers."""
        tickers = ["AAPL", "INVALID12345", "MSFT", "TOOLONG"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["AAPL", "MSFT"]
        assert invalid == ["INVALID12345", "TOOLONG"]
    
    def test_empty_list(self):
        """Test empty list."""
        valid, invalid = validate_ticker_list([])
        assert valid == []
        assert invalid == []
    
    def test_list_with_whitespace(self):
        """Test list with whitespace."""
        tickers = ["  AAPL  ", "  MSFT  ", "  GOOGL  "]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["AAPL", "MSFT", "GOOGL"]
        assert invalid == []
    
    def test_list_with_empty_strings(self):
        """Test list with empty strings."""
        tickers = ["AAPL", "", "MSFT", "   ", "GOOGL"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["AAPL", "MSFT", "GOOGL"]
        assert invalid == []
    
    def test_case_insensitive(self):
        """Test that validation is case-insensitive."""
        tickers = ["aapl", "MSFT", "GoOgL"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["AAPL", "MSFT", "GOOGL"]
        assert invalid == []
    
    def test_tickers_with_dots(self):
        """Test tickers with dots."""
        tickers = ["BRK.B", "BRK.A", "AAPL"]
        valid, invalid = validate_ticker_list(tickers)
        assert valid == ["BRK.B", "BRK.A", "AAPL"]
        assert invalid == []

