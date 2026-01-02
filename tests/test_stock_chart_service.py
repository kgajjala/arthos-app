"""Tests for stock chart service."""
import pytest
from app.services.stock_chart_service import get_stock_chart_data
from app.database import engine, create_db_and_tables
from sqlmodel import Session


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test."""
    create_db_and_tables()
    yield
    # Cleanup is handled by cache service


class TestStockChartService:
    """Tests for stock chart service."""
    
    def test_get_stock_chart_data_success(self):
        """Test successfully getting chart data for a valid ticker."""
        chart_data = get_stock_chart_data("AAPL")
        
        assert chart_data["ticker"] == "AAPL"
        assert "dates" in chart_data
        assert "candlestick_data" in chart_data
        assert "sma_50" in chart_data
        assert "sma_200" in chart_data
        assert "std_bands" in chart_data
        assert "current_price" in chart_data
        assert "sma_50_current" in chart_data
        assert "sma_200_current" in chart_data
        
        # Check that we have data (should be up to 365 days for display)
        assert len(chart_data["dates"]) > 0
        assert len(chart_data["dates"]) <= 365  # Only last 365 days displayed
        assert len(chart_data["candlestick_data"]) > 0
        assert len(chart_data["sma_50"]) > 0
        assert len(chart_data["sma_200"]) > 0
        
        # Check STD bands structure
        assert "std_1_upper" in chart_data["std_bands"]
        assert "std_1_lower" in chart_data["std_bands"]
        assert "std_2_upper" in chart_data["std_bands"]
        assert "std_2_lower" in chart_data["std_bands"]
        
        # Check candlestick data structure
        first_candle = chart_data["candlestick_data"][0]
        assert "x" in first_candle
        assert "open" in first_candle
        assert "high" in first_candle
        assert "low" in first_candle
        assert "close" in first_candle
        
        # Check SMA data structure
        first_sma50 = chart_data["sma_50"][0]
        assert "x" in first_sma50
        assert "y" in first_sma50
        
        # Check that current price is a number
        assert isinstance(chart_data["current_price"], (int, float))
        assert chart_data["current_price"] > 0
        
        # Check that SMAs are numbers
        assert isinstance(chart_data["sma_50_current"], (int, float))
        assert isinstance(chart_data["sma_200_current"], (int, float))
    
    def test_get_stock_chart_data_invalid_ticker(self):
        """Test getting chart data for invalid ticker."""
        with pytest.raises(ValueError):
            get_stock_chart_data("INVALIDTICKER12345")
    
    def test_get_stock_chart_data_candlestick_structure(self):
        """Test that candlestick data has correct structure."""
        chart_data = get_stock_chart_data("MSFT")
        
        # Check all candles have required fields
        for candle in chart_data["candlestick_data"]:
            assert "x" in candle
            assert "open" in candle
            assert "high" in candle
            assert "low" in candle
            assert "close" in candle
            
            # Check that high >= low
            assert candle["high"] >= candle["low"]
            # Check that high >= open and close
            assert candle["high"] >= candle["open"]
            assert candle["high"] >= candle["close"]
            # Check that low <= open and close
            assert candle["low"] <= candle["open"]
            assert candle["low"] <= candle["close"]
    
    def test_get_stock_chart_data_sma_structure(self):
        """Test that SMA data has correct structure."""
        chart_data = get_stock_chart_data("GOOGL")
        
        # Check SMA 50 structure
        for sma_point in chart_data["sma_50"]:
            assert "x" in sma_point
            assert "y" in sma_point
            # y can be None for early days, or a number
            assert sma_point["y"] is None or isinstance(sma_point["y"], (int, float))
        
        # Check SMA 200 structure
        for sma_point in chart_data["sma_200"]:
            assert "x" in sma_point
            assert "y" in sma_point
            # y can be None for early days, or a number
            assert sma_point["y"] is None or isinstance(sma_point["y"], (int, float))
    
    def test_get_stock_chart_data_std_bands_structure(self):
        """Test that STD dev bands have correct structure."""
        chart_data = get_stock_chart_data("MSFT")
        
        std_bands = chart_data["std_bands"]
        
        # Check all band arrays exist and have same length
        assert len(std_bands["std_1_upper"]) == len(std_bands["std_1_lower"])
        assert len(std_bands["std_2_upper"]) == len(std_bands["std_2_lower"])
        assert len(std_bands["std_1_upper"]) == len(chart_data["dates"])
        
        # Check structure of band data points
        for band_point in std_bands["std_1_upper"]:
            assert "x" in band_point
            assert "y" in band_point
            # y can be None or a number
            assert band_point["y"] is None or isinstance(band_point["y"], (int, float))
    
    def test_get_stock_chart_data_dates_match(self):
        """Test that dates match across all data arrays."""
        chart_data = get_stock_chart_data("TSLA")
        
        dates = chart_data["dates"]
        candlestick_dates = [c["x"] for c in chart_data["candlestick_data"]]
        sma50_dates = [s["x"] for s in chart_data["sma_50"]]
        sma200_dates = [s["x"] for s in chart_data["sma_200"]]
        std1_upper_dates = [s["x"] for s in chart_data["std_bands"]["std_1_upper"]]
        std1_lower_dates = [s["x"] for s in chart_data["std_bands"]["std_1_lower"]]
        std2_upper_dates = [s["x"] for s in chart_data["std_bands"]["std_2_upper"]]
        std2_lower_dates = [s["x"] for s in chart_data["std_bands"]["std_2_lower"]]
        
        # All should have the same length
        assert len(dates) == len(candlestick_dates)
        assert len(dates) == len(sma50_dates)
        assert len(dates) == len(sma200_dates)
        assert len(dates) == len(std1_upper_dates)
        assert len(dates) == len(std1_lower_dates)
        assert len(dates) == len(std2_upper_dates)
        assert len(dates) == len(std2_lower_dates)
        
        # All should have matching dates
        assert dates == candlestick_dates
        assert dates == sma50_dates
        assert dates == sma200_dates
        assert dates == std1_upper_dates
        assert dates == std1_lower_dates
        assert dates == std2_upper_dates
        assert dates == std2_lower_dates

