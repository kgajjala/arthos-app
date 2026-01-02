"""Tests for portfolio service."""
import pytest
from uuid import UUID
from datetime import datetime
from app.services.portfolio_service import (
    validate_portfolio_name,
    create_portfolio,
    get_all_portfolios,
    get_portfolio,
    update_portfolio_name,
    delete_portfolio,
    add_stocks_to_portfolio,
    remove_stock_from_portfolio,
    get_portfolio_stocks
)
from app.database import engine, create_db_and_tables
from sqlmodel import Session
from app.models.portfolio import Portfolio, PortfolioStock


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test."""
    create_db_and_tables()
    yield
    # Cleanup
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


class TestValidatePortfolioName:
    """Tests for validate_portfolio_name function."""
    
    def test_valid_name_alphanumeric(self):
        """Test valid alphanumeric name."""
        assert validate_portfolio_name("MyPortfolio123") is True
    
    def test_valid_name_with_spaces(self):
        """Test valid name with spaces."""
        assert validate_portfolio_name("My Portfolio 123") is True
    
    def test_invalid_empty_string(self):
        """Test empty string."""
        assert validate_portfolio_name("") is False
        assert validate_portfolio_name("   ") is False
    
    def test_invalid_too_long(self):
        """Test name that's too long."""
        long_name = "A" * 129  # 129 characters
        assert validate_portfolio_name(long_name) is False
    
    def test_invalid_special_characters(self):
        """Test name with special characters."""
        assert validate_portfolio_name("My-Portfolio") is False
        assert validate_portfolio_name("My_Portfolio") is False
        assert validate_portfolio_name("My@Portfolio") is False
        assert validate_portfolio_name("My.Portfolio") is False


class TestCreatePortfolio:
    """Tests for create_portfolio function."""
    
    def test_create_portfolio_success(self):
        """Test successful portfolio creation."""
        portfolio = create_portfolio("Test Portfolio")
        
        assert portfolio.portfolio_id is not None
        assert portfolio.portfolio_name == "Test Portfolio"
        assert isinstance(portfolio.date_added, datetime)
        assert isinstance(portfolio.date_modified, datetime)
    
    def test_create_portfolio_invalid_name(self):
        """Test portfolio creation with invalid name."""
        with pytest.raises(ValueError, match="Portfolio name must be"):
            create_portfolio("My-Portfolio!")
    
    def test_create_portfolio_whitespace_trimmed(self):
        """Test that portfolio name whitespace is trimmed."""
        portfolio = create_portfolio("  Test Portfolio  ")
        assert portfolio.portfolio_name == "Test Portfolio"


class TestGetAllPortfolios:
    """Tests for get_all_portfolios function."""
    
    def test_get_all_portfolios_empty(self):
        """Test getting all portfolios when none exist."""
        portfolios = get_all_portfolios()
        assert portfolios == []
    
    def test_get_all_portfolios_multiple(self):
        """Test getting all portfolios."""
        portfolio1 = create_portfolio("Portfolio 1")
        portfolio2 = create_portfolio("Portfolio 2")
        
        portfolios = get_all_portfolios()
        assert len(portfolios) == 2
        assert any(p.portfolio_id == portfolio1.portfolio_id for p in portfolios)
        assert any(p.portfolio_id == portfolio2.portfolio_id for p in portfolios)


class TestGetPortfolio:
    """Tests for get_portfolio function."""
    
    def test_get_portfolio_success(self):
        """Test getting a portfolio by ID."""
        created = create_portfolio("Test Portfolio")
        retrieved = get_portfolio(created.portfolio_id)
        
        assert retrieved.portfolio_id == created.portfolio_id
        assert retrieved.portfolio_name == "Test Portfolio"
    
    def test_get_portfolio_not_found(self):
        """Test getting a non-existent portfolio."""
        fake_id = UUID('00000000-0000-0000-0000-000000000000')
        with pytest.raises(ValueError, match="not found"):
            get_portfolio(fake_id)


class TestUpdatePortfolioName:
    """Tests for update_portfolio_name function."""
    
    def test_update_portfolio_name_success(self):
        """Test successful portfolio name update."""
        portfolio = create_portfolio("Old Name")
        updated = update_portfolio_name(portfolio.portfolio_id, "New Name")
        
        assert updated.portfolio_name == "New Name"
        assert updated.portfolio_id == portfolio.portfolio_id
        assert updated.date_modified > portfolio.date_modified
    
    def test_update_portfolio_name_invalid(self):
        """Test updating with invalid name."""
        portfolio = create_portfolio("Test Portfolio")
        with pytest.raises(ValueError, match="Portfolio name must be"):
            update_portfolio_name(portfolio.portfolio_id, "Invalid-Name!")


class TestDeletePortfolio:
    """Tests for delete_portfolio function."""
    
    def test_delete_portfolio_success(self):
        """Test successful portfolio deletion."""
        portfolio = create_portfolio("Test Portfolio")
        result = delete_portfolio(portfolio.portfolio_id)
        
        assert result is True
        
        # Verify portfolio is deleted
        with pytest.raises(ValueError, match="not found"):
            get_portfolio(portfolio.portfolio_id)


class TestAddStocksToPortfolio:
    """Tests for add_stocks_to_portfolio function."""
    
    def test_add_stocks_success(self):
        """Test successfully adding stocks to portfolio."""
        portfolio = create_portfolio("Test Portfolio")
        added = add_stocks_to_portfolio(portfolio.portfolio_id, ["AAPL", "MSFT"])
        
        assert len(added) == 2
        assert any(s.ticker == "AAPL" for s in added)
        assert any(s.ticker == "MSFT" for s in added)
    
    def test_add_stocks_duplicate_ignored(self):
        """Test that duplicate stocks are ignored."""
        portfolio = create_portfolio("Test Portfolio")
        
        # Add AAPL first time
        added1 = add_stocks_to_portfolio(portfolio.portfolio_id, ["AAPL"])
        assert len(added1) == 1
        
        # Try to add AAPL again
        added2 = add_stocks_to_portfolio(portfolio.portfolio_id, ["AAPL"])
        assert len(added2) == 0  # Should be ignored
    
    def test_add_stocks_invalid_ticker(self):
        """Test adding invalid ticker format."""
        portfolio = create_portfolio("Test Portfolio")
        with pytest.raises(ValueError, match="Invalid ticker format"):
            add_stocks_to_portfolio(portfolio.portfolio_id, ["INVALID12345"])


class TestRemoveStockFromPortfolio:
    """Tests for remove_stock_from_portfolio function."""
    
    def test_remove_stock_success(self):
        """Test successfully removing a stock."""
        portfolio = create_portfolio("Test Portfolio")
        add_stocks_to_portfolio(portfolio.portfolio_id, ["AAPL", "MSFT"])
        
        result = remove_stock_from_portfolio(portfolio.portfolio_id, "AAPL")
        assert result is True
        
        # Verify stock is removed
        stocks = get_portfolio_stocks(portfolio.portfolio_id)
        assert len(stocks) == 1
        assert stocks[0].ticker == "MSFT"
    
    def test_remove_stock_not_found(self):
        """Test removing a stock that doesn't exist."""
        portfolio = create_portfolio("Test Portfolio")
        with pytest.raises(ValueError, match="not found in portfolio"):
            remove_stock_from_portfolio(portfolio.portfolio_id, "AAPL")
