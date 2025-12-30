"""Tests for FMP service module."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.services.fmp_service import (
    fetch_fmp_stock_data,
    get_fmp_stock_metrics,
    get_fmp_multiple_stock_metrics
)
from app.services.fmp_cache_service import get_fmp_cached_data, set_fmp_cached_data
from app.database import engine, create_db_and_tables
from sqlmodel import Session
from app.models.fmp_cache import FMPCache


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test."""
    create_db_and_tables()
    yield
    # Cleanup: delete all cache entries after each test
    with Session(engine) as session:
        from sqlmodel import select
        statement = select(FMPCache)
        all_entries = session.exec(statement).all()
        for entry in all_entries:
            session.delete(entry)
        session.commit()


class TestFetchFMPStockData:
    """Tests for fetch_fmp_stock_data function."""
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_success_list_format(self, mock_get):
        """Test successful FMP API data fetch with new list format."""
        # Mock FMP API response (new format returns list directly)
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "date": "2024-12-24",
                "close": 150.0,
                "open": 149.0,
                "high": 151.0,
                "low": 148.0,
                "volume": 1000000
            },
            {
                "date": "2024-12-23",
                "close": 149.0,
                "open": 148.0,
                "high": 150.0,
                "low": 147.0,
                "volume": 1100000
            }
        ]
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = fetch_fmp_stock_data("AAPL")
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert 'Close' in data.columns
        assert len(data) == 2
        mock_get.assert_called_once()
        # Verify correct endpoint is used
        call_args = mock_get.call_args
        assert "/historical-price-eod/full" in call_args[0][0]
        assert call_args[1]["params"]["symbol"] == "AAPL"
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_success_dict_format(self, mock_get):
        """Test successful FMP API data fetch with old dict format (backward compatibility)."""
        # Mock FMP API response (old format)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2024-12-24",
                    "close": 150.0,
                    "open": 149.0,
                    "high": 151.0,
                    "low": 148.0,
                    "volume": 1000000
                }
            ]
        }
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = fetch_fmp_stock_data("AAPL")
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert 'Close' in data.columns
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_error_message(self, mock_get):
        """Test FMP API error message handling."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Error Message": "Invalid API key"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="FMP API error"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_no_historical_list(self, mock_get):
        """Test FMP API response with empty list (no historical data)."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="No historical data found"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_no_historical_dict(self, mock_get):
        """Test FMP API response with no historical data (dict format)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "historical": []
        }
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="No historical data found"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.FMP_API_KEY', '***MASKED***')
    def test_fetch_fmp_stock_data_no_api_key(self):
        """Test that missing API key raises error."""
        with pytest.raises(ValueError, match="FMP API key is not configured"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_rate_limit(self, mock_get):
        """Test handling of rate limit (429) error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="rate limit exceeded"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_invalid_api_key(self, mock_get):
        """Test handling of invalid API key (403) error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.reason = "Forbidden"
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="FMP API key is invalid or missing"):
            fetch_fmp_stock_data("AAPL")
    
    @patch('app.services.fmp_service.requests.get')
    @patch('app.services.fmp_service.FMP_API_KEY', 'test_api_key')
    def test_fetch_fmp_stock_data_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(ValueError, match="FMP API request failed"):
            fetch_fmp_stock_data("AAPL")


class TestGetFMPStockMetrics:
    """Tests for get_fmp_stock_metrics function."""
    
    @patch('app.services.fmp_service.fetch_fmp_stock_data')
    def test_get_fmp_metrics_uses_cache_when_available(self, mock_fetch):
        """Test that get_fmp_stock_metrics uses cache when available."""
        # Create cached data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        cached_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        set_fmp_cached_data("AAPL", cached_data)
        
        # Call get_fmp_stock_metrics
        metrics = get_fmp_stock_metrics("AAPL")
        
        # Verify FMP API was NOT called
        mock_fetch.assert_not_called()
        
        # Verify metrics are returned
        assert metrics["ticker"] == "AAPL"
        assert "cached" in metrics
        assert metrics["cached"] is True
        assert "cache_timestamp" in metrics
    
    @patch('app.services.fmp_service.fetch_fmp_stock_data')
    def test_get_fmp_metrics_fetches_when_cache_missing(self, mock_fetch):
        """Test that get_fmp_stock_metrics fetches from FMP when cache is missing."""
        # Mock FMP API response
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        mock_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        mock_fetch.return_value = mock_data
        
        # Call get_fmp_stock_metrics
        metrics = get_fmp_stock_metrics("AAPL")
        
        # Verify FMP API was called
        mock_fetch.assert_called_once_with("AAPL")
        
        # Verify metrics are returned
        assert metrics["ticker"] == "AAPL"
        assert "cached" in metrics
        assert metrics["cached"] is False
        assert "cache_timestamp" not in metrics
        
        # Verify data was cached
        cached_result = get_fmp_cached_data("AAPL")
        assert cached_result is not None
    
    @patch('app.services.fmp_service.fetch_fmp_stock_data')
    def test_get_fmp_metrics_uses_cache_when_api_fails(self, mock_fetch):
        """Test that cache is used when API fails but cache exists."""
        # Create cached data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        cached_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        set_fmp_cached_data("AAPL", cached_data)
        
        # Mock API failure
        mock_fetch.side_effect = ValueError("API error")
        
        # Should still work using cache
        metrics = get_fmp_stock_metrics("AAPL")
        
        assert metrics["cached"] is True
        assert metrics["ticker"] == "AAPL"
    
    @patch('app.services.fmp_service.fetch_fmp_stock_data')
    def test_get_fmp_metrics_fails_when_no_cache_and_api_fails(self, mock_fetch):
        """Test that error is raised when API fails and no cache exists."""
        # Mock API failure
        mock_fetch.side_effect = ValueError("API error")
        
        # Should raise error
        with pytest.raises(ValueError, match="Failed to fetch data and no cache available"):
            get_fmp_stock_metrics("AAPL")
    
    def test_get_fmp_metrics_cache_timestamp_format(self):
        """Test that cache_timestamp is in ISO format when cached."""
        # Create cached data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        cached_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        set_fmp_cached_data("AAPL", cached_data)
        
        # Call get_fmp_stock_metrics
        metrics = get_fmp_stock_metrics("AAPL")
        
        # Verify cache_timestamp is present and in ISO format
        assert "cache_timestamp" in metrics
        assert isinstance(metrics["cache_timestamp"], str)
        # Verify it's a valid ISO format by parsing it
        parsed = datetime.fromisoformat(metrics["cache_timestamp"])
        assert isinstance(parsed, datetime)


class TestGetFMPMultipleStockMetrics:
    """Tests for get_fmp_multiple_stock_metrics function."""
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_multiple_metrics_single_ticker(self, mock_get_metrics):
        """Test getting metrics for a single ticker."""
        mock_get_metrics.return_value = {
            "ticker": "AAPL",
            "sma_50": 150.0,
            "sma_200": 145.0,
            "devstep": 1.0,
            "signal": "Neutral",
            "current_price": 155.0,
            "data_points": 250,
            "cached": False
        }
        
        results = get_fmp_multiple_stock_metrics(["AAPL"])
        
        assert len(results) == 1
        assert "ticker" in results[0]
        assert results[0]["ticker"] == "AAPL"
        assert "error" not in results[0]
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_multiple_metrics_multiple_tickers(self, mock_get_metrics):
        """Test getting metrics for multiple tickers."""
        def side_effect(ticker):
            return {
                "ticker": ticker,
                "sma_50": 150.0,
                "sma_200": 145.0,
                "devstep": 1.0,
                "signal": "Neutral",
                "current_price": 155.0,
                "data_points": 250,
                "cached": False
            }
        
        mock_get_metrics.side_effect = side_effect
        
        results = get_fmp_multiple_stock_metrics(["AAPL", "MSFT"])
        
        assert len(results) == 2
        assert all("ticker" in r for r in results)
        assert any(r["ticker"] == "AAPL" for r in results)
        assert any(r["ticker"] == "MSFT" for r in results)
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_multiple_metrics_invalid_ticker(self, mock_get_metrics):
        """Test handling of invalid ticker."""
        mock_get_metrics.side_effect = ValueError("Invalid ticker")
        
        results = get_fmp_multiple_stock_metrics(["INVALIDTICKER12345"])
        
        assert len(results) == 1
        assert "error" in results[0]
        assert results[0]["ticker"] == "INVALIDTICKER12345"
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_multiple_metrics_mixed_valid_invalid(self, mock_get_metrics):
        """Test handling of mixed valid and invalid tickers."""
        def side_effect(ticker):
            if ticker == "INVALID":
                raise ValueError("Invalid ticker")
            return {
                "ticker": ticker,
                "sma_50": 150.0,
                "sma_200": 145.0,
                "devstep": 1.0,
                "signal": "Neutral",
                "current_price": 155.0,
                "data_points": 250,
                "cached": False
            }
        
        mock_get_metrics.side_effect = side_effect
        
        results = get_fmp_multiple_stock_metrics(["AAPL", "INVALID", "MSFT"])
        
        assert len(results) == 3
        assert any("error" in r for r in results)
        assert any("error" not in r for r in results)
    
    def test_get_fmp_multiple_metrics_empty_list(self):
        """Test handling of empty ticker list."""
        results = get_fmp_multiple_stock_metrics([])
        assert len(results) == 0
    
    def test_get_fmp_multiple_metrics_whitespace_handling(self):
        """Test that whitespace in tickers is handled correctly."""
        with patch('app.services.fmp_service.get_fmp_stock_metrics') as mock_get_metrics:
            def side_effect(ticker):
                return {
                    "ticker": ticker,
                    "sma_50": 150.0,
                    "sma_200": 145.0,
                    "devstep": 1.0,
                    "signal": "Neutral",
                    "current_price": 155.0,
                    "data_points": 250,
                    "cached": False
                }
            mock_get_metrics.side_effect = side_effect
            
            results = get_fmp_multiple_stock_metrics(["  AAPL  ", "  MSFT  "])
            
            assert len(results) == 2
            assert all(r["ticker"] in ["AAPL", "MSFT"] for r in results if "error" not in r)

