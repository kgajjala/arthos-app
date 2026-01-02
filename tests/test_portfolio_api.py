"""Tests for portfolio API endpoints."""
import pytest
from fastapi import status
from uuid import UUID
from app.services.portfolio_service import create_portfolio, add_stocks_to_portfolio
from app.database import engine, create_db_and_tables
from sqlmodel import Session
from app.models.portfolio import Portfolio, PortfolioStock


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables and clean up before and after each test."""
    create_db_and_tables()
    
    # Cleanup before test: delete all entries
    with Session(engine) as session:
        from sqlmodel import select
        statement = select(PortfolioStock)
        all_stocks = session.exec(statement).all()
        for stock in all_stocks:
            session.delete(stock)
        
        statement = select(Portfolio)
        all_portfolios = session.exec(statement).all()
        for portfolio in all_portfolios:
            session.delete(portfolio)
        
        session.commit()
    
    yield
    
    # Cleanup after test: delete all entries
    with Session(engine) as session:
        from sqlmodel import select
        statement = select(PortfolioStock)
        all_stocks = session.exec(statement).all()
        for stock in all_stocks:
            session.delete(stock)
        
        statement = select(Portfolio)
        all_portfolios = session.exec(statement).all()
        for portfolio in all_portfolios:
            session.delete(portfolio)
        
        session.commit()


class TestPortfolioAPI:
    """Tests for /v1/portfolio endpoints."""
    
    def test_create_portfolio_success(self, client):
        """Test creating a portfolio via API."""
        response = client.post(
            "/v1/portfolio",
            json={"portfolio_name": "Test Portfolio"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "portfolio_id" in data
        assert data["portfolio_name"] == "Test Portfolio"
        assert "date_added" in data
        assert "date_modified" in data
    
    def test_create_portfolio_invalid_name(self, client):
        """Test creating portfolio with invalid name."""
        response = client.post(
            "/v1/portfolio",
            json={"portfolio_name": "Invalid-Name!"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
    
    def test_list_portfolios_empty(self, client):
        """Test listing portfolios when none exist."""
        response = client.get("/v1/portfolio")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "portfolios" in data
        assert data["portfolios"] == []
    
    def test_list_portfolios_multiple(self, client):
        """Test listing multiple portfolios."""
        # Create portfolios
        create_portfolio("Portfolio 1")
        create_portfolio("Portfolio 2")
        
        response = client.get("/v1/portfolio")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["portfolios"]) == 2
    
    def test_get_portfolio_success(self, client):
        """Test getting a portfolio by ID."""
        portfolio = create_portfolio("Test Portfolio")
        
        response = client.get(f"/v1/portfolio/{portfolio.portfolio_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["portfolio_id"] == str(portfolio.portfolio_id)
        assert data["portfolio_name"] == "Test Portfolio"
        assert "stocks" in data
    
    def test_get_portfolio_not_found(self, client):
        """Test getting a non-existent portfolio."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/v1/portfolio/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_portfolio_name(self, client):
        """Test updating portfolio name."""
        portfolio = create_portfolio("Old Name")
        
        response = client.put(
            f"/v1/portfolio/{portfolio.portfolio_id}",
            json={"portfolio_name": "New Name"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["portfolio_name"] == "New Name"
    
    def test_delete_portfolio(self, client):
        """Test deleting a portfolio."""
        portfolio = create_portfolio("Test Portfolio")
        
        response = client.delete(f"/v1/portfolio/{portfolio.portfolio_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
        # Verify portfolio is deleted
        get_response = client.get(f"/v1/portfolio/{portfolio.portfolio_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_add_stocks_to_portfolio(self, client):
        """Test adding stocks to a portfolio."""
        portfolio = create_portfolio("Test Portfolio")
        
        response = client.post(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks",
            json={"tickers": "AAPL,MSFT"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "added_stocks" in data
        assert len(data["added_stocks"]) == 2
    
    def test_add_stocks_duplicate_ignored(self, client):
        """Test that duplicate stocks are ignored."""
        portfolio = create_portfolio("Test Portfolio")
        
        # Add AAPL first time
        response1 = client.post(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks",
            json={"tickers": "AAPL"}
        )
        assert response1.status_code == status.HTTP_200_OK
        assert len(response1.json()["added_stocks"]) == 1
        
        # Try to add AAPL again
        response2 = client.post(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks",
            json={"tickers": "AAPL"}
        )
        assert response2.status_code == status.HTTP_200_OK
        assert len(response2.json()["added_stocks"]) == 0  # Should be ignored
    
    def test_add_stocks_invalid_ticker(self, client):
        """Test adding invalid ticker format."""
        portfolio = create_portfolio("Test Portfolio")
        
        response = client.post(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks",
            json={"tickers": "INVALID12345"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_remove_stock_from_portfolio(self, client):
        """Test removing a stock from portfolio."""
        portfolio = create_portfolio("Test Portfolio")
        add_stocks_to_portfolio(portfolio.portfolio_id, ["AAPL", "MSFT"])
        
        response = client.delete(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks/AAPL"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
    
    def test_remove_stock_not_found(self, client):
        """Test removing a stock that doesn't exist."""
        portfolio = create_portfolio("Test Portfolio")
        
        response = client.delete(
            f"/v1/portfolio/{portfolio.portfolio_id}/stocks/AAPL"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
