"""Tests for portfolio models."""
import pytest
from datetime import datetime
from uuid import uuid4
from app.models.portfolio import Portfolio, PortfolioStock
from app.database import engine, create_db_and_tables
from sqlmodel import Session


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test."""
    create_db_and_tables()
    yield
    # Cleanup: delete all entries after each test
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


class TestPortfolio:
    """Tests for Portfolio model."""
    
    def test_create_portfolio(self):
        """Test creating a portfolio."""
        with Session(engine) as session:
            portfolio = Portfolio(
                portfolio_name="Test Portfolio",
                date_added=datetime.now(),
                date_modified=datetime.now()
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)
            
            assert portfolio.portfolio_id is not None
            assert portfolio.portfolio_name == "Test Portfolio"
            assert isinstance(portfolio.date_added, datetime)
            assert isinstance(portfolio.date_modified, datetime)
    
    def test_portfolio_name_max_length(self):
        """Test portfolio name respects max length."""
        with Session(engine) as session:
            # 128 characters should work
            long_name = "A" * 128
            portfolio = Portfolio(
                portfolio_name=long_name,
                date_added=datetime.now(),
                date_modified=datetime.now()
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)
            
            assert len(portfolio.portfolio_name) == 128


class TestPortfolioStock:
    """Tests for PortfolioStock model."""
    
    def test_create_portfolio_stock(self):
        """Test creating a portfolio stock."""
        with Session(engine) as session:
            # Create portfolio first
            portfolio = Portfolio(
                portfolio_name="Test Portfolio",
                date_added=datetime.now(),
                date_modified=datetime.now()
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)
            
            # Create portfolio stock
            stock = PortfolioStock(
                portfolio_id=portfolio.portfolio_id,
                ticker="AAPL",
                date_added=datetime.now()
            )
            session.add(stock)
            session.commit()
            session.refresh(stock)
            
            assert stock.portfolio_id == portfolio.portfolio_id
            assert stock.ticker == "AAPL"
            assert isinstance(stock.date_added, datetime)
    
    def test_portfolio_stock_composite_key(self):
        """Test that portfolio_id and ticker form composite primary key."""
        with Session(engine) as session:
            # Create portfolio
            portfolio = Portfolio(
                portfolio_name="Test Portfolio",
                date_added=datetime.now(),
                date_modified=datetime.now()
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)
            
            # Create first stock
            stock1 = PortfolioStock(
                portfolio_id=portfolio.portfolio_id,
                ticker="AAPL",
                date_added=datetime.now()
            )
            session.add(stock1)
            session.commit()
            
            # Try to create duplicate (same portfolio_id and ticker)
            # This should fail due to primary key constraint
            stock2 = PortfolioStock(
                portfolio_id=portfolio.portfolio_id,
                ticker="AAPL",
                date_added=datetime.now()
            )
            session.add(stock2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                session.commit()
