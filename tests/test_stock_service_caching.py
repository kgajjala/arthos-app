"""Tests for stock service caching functionality."""
import pytest
from app.services.stock_service import get_stock_metrics
from app.services.cache_service import get_cached_data, set_cached_data
from app.database import engine, create_db_and_tables
from sqlmodel import Session
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test."""
    create_db_and_tables()
    yield
    # Cleanup: delete all cache entries after each test
    with Session(engine) as session:
        from sqlmodel import select
        from app.models.stock_cache import StockCache
        statement = select(StockCache)
        all_entries = session.exec(statement).all()
        for entry in all_entries:
            session.delete(entry)
        session.commit()


class TestStockServiceCaching:
    """Tests for caching in stock service."""
    
    @patch('app.services.stock_service.fetch_stock_data')
    def test_get_stock_metrics_uses_cache_when_available(self, mock_fetch):
        """Test that get_stock_metrics uses cache when available."""
        # Create cached data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        cached_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        set_cached_data("AAPL", cached_data)
        
        # Call get_stock_metrics
        metrics = get_stock_metrics("AAPL")
        
        # Verify yfinance was NOT called
        mock_fetch.assert_not_called()
        
        # Verify metrics are returned
        assert metrics["ticker"] == "AAPL"
        assert "cached" in metrics
        assert metrics["cached"] is True
        assert "cache_timestamp" in metrics
    
    @patch('app.services.stock_service.fetch_stock_data')
    def test_get_stock_metrics_fetches_when_cache_missing(self, mock_fetch):
        """Test that get_stock_metrics fetches from yfinance when cache is missing."""
        # Mock yfinance response
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        mock_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        mock_fetch.return_value = mock_data
        
        # Call get_stock_metrics
        metrics = get_stock_metrics("AAPL")
        
        # Verify yfinance was called
        mock_fetch.assert_called_once_with("AAPL")
        
        # Verify metrics are returned
        assert metrics["ticker"] == "AAPL"
        assert "cached" in metrics
        assert metrics["cached"] is False
        assert "cache_timestamp" not in metrics
        
        # Verify data was cached
        cached_result = get_cached_data("AAPL")
        assert cached_result is not None
    
    @patch('app.services.stock_service.fetch_stock_data')
    def test_get_stock_metrics_fetches_when_cache_expired(self, mock_fetch):
        """Test that get_stock_metrics fetches when cache is expired."""
        # Create expired cache entry
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        expired_data = pd.DataFrame({
            'Close': [100.0] * 100
        }, index=dates)
        
        # Manually create expired entry
        with Session(engine) as session:
            from app.models.stock_cache import StockCache
            import json
            data_dict = expired_data.to_dict(orient='index')
            data_dict = {str(k): v for k, v in data_dict.items()}
            data_json = json.dumps(data_dict)
            
            expired_entry = StockCache(
                ticker="AAPL",
                data=data_json,
                cache_timestamp=datetime.now() - timedelta(hours=25)  # Expired
            )
            session.add(expired_entry)
            session.commit()
        
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Close': [200.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        mock_fetch.return_value = mock_data
        
        # Call get_stock_metrics
        metrics = get_stock_metrics("AAPL")
        
        # Verify yfinance was called (cache was expired)
        mock_fetch.assert_called_once_with("AAPL")
        
        # Verify metrics indicate not cached
        assert metrics["cached"] is False
    
    def test_get_stock_metrics_cache_timestamp_format(self):
        """Test that cache_timestamp is in ISO format when cached."""
        # Create cached data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        cached_data = pd.DataFrame({
            'Close': [100.0 + i * 0.1 for i in range(100)]
        }, index=dates)
        set_cached_data("AAPL", cached_data)
        
        # Call get_stock_metrics
        metrics = get_stock_metrics("AAPL")
        
        # Verify cache_timestamp is present and in ISO format
        assert "cache_timestamp" in metrics
        assert isinstance(metrics["cache_timestamp"], str)
        # Verify it's a valid ISO format by parsing it
        from datetime import datetime
        parsed = datetime.fromisoformat(metrics["cache_timestamp"])
        assert isinstance(parsed, datetime)

