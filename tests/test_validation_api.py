"""Tests for ticker validation API endpoint."""
import pytest
from fastapi import status


class TestValidateTickersAPI:
    """Tests for /validate/tickers endpoint."""
    
    def test_validate_tickers_all_valid(self, client):
        """Test validation endpoint with all valid tickers."""
        response = client.get("/validate/tickers?tickers=AAPL,MSFT,GOOGL")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "valid" in data
        assert "invalid" in data
        assert len(data["valid"]) == 3
        assert len(data["invalid"]) == 0
        assert "AAPL" in data["valid"]
        assert "MSFT" in data["valid"]
        assert "GOOGL" in data["valid"]
    
    def test_validate_tickers_all_invalid(self, client):
        """Test validation endpoint with all invalid tickers."""
        response = client.get("/validate/tickers?tickers=INVALID12345,TOOLONG")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "valid" in data
        assert "invalid" in data
        assert len(data["valid"]) == 0
        assert len(data["invalid"]) == 2
        assert any(item["ticker"] == "INVALID12345" for item in data["invalid"])
        assert any(item["ticker"] == "TOOLONG" for item in data["invalid"])
    
    def test_validate_tickers_mixed(self, client):
        """Test validation endpoint with mixed valid and invalid tickers."""
        response = client.get("/validate/tickers?tickers=AAPL,INVALID12345,MSFT")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "valid" in data
        assert "invalid" in data
        assert len(data["valid"]) == 2
        assert len(data["invalid"]) == 1
        assert "AAPL" in data["valid"]
        assert "MSFT" in data["valid"]
        assert any(item["ticker"] == "INVALID12345" for item in data["invalid"])
    
    def test_validate_tickers_empty(self, client):
        """Test validation endpoint with empty tickers."""
        response = client.get("/validate/tickers?tickers=")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "valid" in data
        assert "invalid" in data
        assert len(data["valid"]) == 0
        assert len(data["invalid"]) == 0
    
    def test_validate_tickers_missing_param(self, client):
        """Test validation endpoint without query parameter."""
        response = client.get("/validate/tickers")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_validate_tickers_with_whitespace(self, client):
        """Test validation endpoint with whitespace in tickers."""
        response = client.get("/validate/tickers?tickers=  AAPL  ,  MSFT  ")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["valid"]) == 2
        assert "AAPL" in data["valid"]
        assert "MSFT" in data["valid"]
    
    def test_validate_tickers_case_insensitive(self, client):
        """Test that validation is case-insensitive."""
        response = client.get("/validate/tickers?tickers=aapl,MSFT,GoOgL")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["valid"]) == 3
        assert "AAPL" in data["valid"]
        assert "MSFT" in data["valid"]
        assert "GOOGL" in data["valid"]
    
    def test_validate_tickers_with_dots(self, client):
        """Test validation with tickers containing dots."""
        response = client.get("/validate/tickers?tickers=BRK.B,BRK.A,AAPL")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["valid"]) == 3
        assert "BRK.B" in data["valid"]
        assert "BRK.A" in data["valid"]
        assert "AAPL" in data["valid"]

