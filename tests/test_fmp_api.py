"""Tests for FMP API endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch
from app.services.fmp_service import get_fmp_stock_metrics


class TestFMPStockAPI:
    """Tests for /v2/stock endpoint."""
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_stock_data_valid_ticker(self, mock_get_metrics, client):
        """Test API endpoint with a valid ticker."""
        mock_get_metrics.return_value = {
            "ticker": "AAPL",
            "sma_50": 150.25,
            "sma_200": 145.80,
            "devstep": 1.2345,
            "signal": "Overbought",
            "current_price": 155.50,
            "data_points": 252,
            "cached": False
        }
        
        response = client.get("/v2/stock?q=AAPL")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "ticker" in data
        assert "sma_50" in data
        assert "sma_200" in data
        assert "devstep" in data
        assert "signal" in data
        assert "current_price" in data
        assert "data_points" in data
        assert "cached" in data
    
    def test_get_fmp_stock_data_missing_query_param(self, client):
        """Test API endpoint without query parameter."""
        response = client.get("/v2/stock")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_fmp_stock_data_empty_query_param(self, client):
        """Test API endpoint with empty query parameter."""
        response = client.get("/v2/stock?q=")
        
        # Should return 400 or 422
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_stock_data_invalid_ticker(self, mock_get_metrics, client):
        """Test API endpoint with invalid ticker."""
        mock_get_metrics.side_effect = ValueError("FMP API error: Invalid ticker")
        
        response = client.get("/v2/stock?q=INVALIDTICKER12345")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        # Verify FMP error message is passed through
        assert "FMP API error" in data["detail"] or "Invalid ticker" in data["detail"]
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_stock_data_case_insensitive(self, mock_get_metrics, client):
        """Test that ticker parameter is case-insensitive."""
        mock_get_metrics.return_value = {
            "ticker": "AAPL",
            "sma_50": 150.25,
            "sma_200": 145.80,
            "devstep": 1.2345,
            "signal": "Overbought",
            "current_price": 155.50,
            "data_points": 252,
            "cached": False
        }
        
        response_lower = client.get("/v2/stock?q=aapl")
        response_upper = client.get("/v2/stock?q=AAPL")
        
        assert response_lower.status_code == status.HTTP_200_OK
        assert response_upper.status_code == status.HTTP_200_OK
        
        # Both should return the same ticker (uppercase)
        assert response_lower.json()["ticker"] == "AAPL"
        assert response_upper.json()["ticker"] == "AAPL"
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_stock_data_with_whitespace(self, mock_get_metrics, client):
        """Test that whitespace in ticker is handled correctly."""
        mock_get_metrics.return_value = {
            "ticker": "AAPL",
            "sma_50": 150.25,
            "sma_200": 145.80,
            "devstep": 1.2345,
            "signal": "Overbought",
            "current_price": 155.50,
            "data_points": 252,
            "cached": False
        }
        
        response = client.get("/v2/stock?q=  AAPL  ")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticker"] == "AAPL"
    
    @patch('app.services.fmp_service.get_fmp_stock_metrics')
    def test_get_fmp_stock_data_error_message_passed_through(self, mock_get_metrics, client):
        """Test that FMP error messages are passed through to UI."""
        mock_get_metrics.side_effect = ValueError("FMP API error: Rate limit exceeded")
        
        response = client.get("/v2/stock?q=AAPL")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        # Verify FMP error message is in the response
        assert "Rate limit exceeded" in data["detail"] or "FMP API error" in data["detail"]

