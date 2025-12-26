"""Tests for stock service module."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.stock_service import (
    fetch_stock_data,
    calculate_sma,
    calculate_devstep,
    calculate_signal,
    get_stock_metrics
)


class TestCalculateSMA:
    """Tests for calculate_sma function."""
    
    def test_sma_with_sufficient_data(self):
        """Test SMA calculation with sufficient data points."""
        # Create sample data with 100 days
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = pd.Series(range(100, 200), index=dates)
        data = pd.DataFrame({'Close': prices})
        
        sma_50 = calculate_sma(data, 50)
        # SMA of last 50 values: (150+151+...+199)/50 = 174.5
        expected = sum(range(150, 200)) / 50
        assert sma_50 == pytest.approx(expected, rel=1e-2)
    
    def test_sma_with_insufficient_data(self):
        """Test SMA calculation when data points are less than window."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        prices = pd.Series(range(100, 130), index=dates)
        data = pd.DataFrame({'Close': prices})
        
        sma_50 = calculate_sma(data, 50)
        # Should use all available data (30 points)
        expected = sum(range(100, 130)) / 30
        assert sma_50 == pytest.approx(expected, rel=1e-2)


class TestCalculateDevstep:
    """Tests for calculate_devstep function."""
    
    def test_devstep_calculation(self):
        """Test devstep calculation."""
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = pd.Series([100.0] * 100, index=dates)  # Constant price
        data = pd.DataFrame({'Close': prices})
        
        sma_50 = 100.0
        devstep = calculate_devstep(data, sma_50)
        
        # With constant prices, std dev is 0, so devstep should be 0
        assert devstep == pytest.approx(0.0, abs=1e-6)
    
    def test_devstep_with_variation(self):
        """Test devstep with price variation."""
        import numpy as np
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        # Create prices with variation - gradually increasing with some noise
        np.random.seed(42)  # For reproducibility
        base_prices = [100.0 + i * 0.1 + np.random.normal(0, 1) for i in range(100)]
        prices = pd.Series(base_prices, index=dates)
        data = pd.DataFrame({'Close': prices})
        
        sma_50 = data['Close'].tail(50).mean()
        devstep = calculate_devstep(data, sma_50)
        
        # With variation, devstep should be a valid number (not NaN or inf)
        assert not (pd.isna(devstep) or np.isinf(devstep))
        assert isinstance(devstep, (int, float))


class TestCalculateSignal:
    """Tests for calculate_signal function."""
    
    def test_signal_neutral(self):
        """Test signal calculation for neutral range."""
        assert calculate_signal(0.0) == "Neutral"
        assert calculate_signal(0.5) == "Neutral"
        assert calculate_signal(-0.5) == "Neutral"
        assert calculate_signal(1.0) == "Neutral"
        assert calculate_signal(-1.0) == "Neutral"
    
    def test_signal_overbought(self):
        """Test signal calculation for overbought range."""
        assert calculate_signal(1.5) == "Overbought"
        assert calculate_signal(2.0) == "Overbought"
    
    def test_signal_extreme_overbought(self):
        """Test signal calculation for extreme overbought."""
        assert calculate_signal(2.1) == "Extreme Overbought"
        assert calculate_signal(3.0) == "Extreme Overbought"
    
    def test_signal_oversold(self):
        """Test signal calculation for oversold range."""
        assert calculate_signal(-1.5) == "Oversold"
        assert calculate_signal(-2.0) == "Oversold"
    
    def test_signal_extreme_oversold(self):
        """Test signal calculation for extreme oversold."""
        assert calculate_signal(-2.1) == "Extreme Oversold"
        assert calculate_signal(-3.0) == "Extreme Oversold"


class TestFetchStockData:
    """Tests for fetch_stock_data function."""
    
    def test_fetch_valid_ticker(self):
        """Test fetching data for a valid ticker."""
        # Use a well-known ticker like AAPL
        data = fetch_stock_data("AAPL")
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert 'Close' in data.columns
    
    def test_fetch_invalid_ticker(self):
        """Test fetching data for an invalid ticker."""
        with pytest.raises(ValueError, match="No data found|Error fetching"):
            fetch_stock_data("INVALIDTICKER12345")


class TestGetStockMetrics:
    """Tests for get_stock_metrics function."""
    
    def test_get_metrics_valid_ticker(self):
        """Test getting metrics for a valid ticker."""
        metrics = get_stock_metrics("AAPL")
        
        assert isinstance(metrics, dict)
        assert "ticker" in metrics
        assert "sma_50" in metrics
        assert "sma_200" in metrics
        assert "devstep" in metrics
        assert "signal" in metrics
        assert "current_price" in metrics
        assert "data_points" in metrics
        
        # Verify signal is one of the expected values
        assert metrics["signal"] in [
            "Neutral", "Overbought", "Extreme Overbought",
            "Oversold", "Extreme Oversold"
        ]
        
        # Verify numeric values are reasonable
        assert metrics["sma_50"] > 0
        assert metrics["sma_200"] > 0
        assert metrics["current_price"] > 0
        assert metrics["data_points"] > 0
    
    def test_get_metrics_invalid_ticker(self):
        """Test getting metrics for an invalid ticker."""
        with pytest.raises(ValueError):
            get_stock_metrics("INVALIDTICKER12345")
    
    def test_ticker_case_insensitive(self):
        """Test that ticker is converted to uppercase."""
        metrics = get_stock_metrics("aapl")
        assert metrics["ticker"] == "AAPL"

