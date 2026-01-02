"""Portfolio models."""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List


class Portfolio(SQLModel, table=True):
    """Portfolio model."""
    __tablename__ = "portfolio"
    
    portfolio_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique portfolio identifier"
    )
    portfolio_name: str = Field(
        max_length=128,
        description="Portfolio name (alphanumeric and spaces only)"
    )
    date_added: datetime = Field(
        default_factory=datetime.now,
        description="When the portfolio was created"
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        description="When the portfolio was last updated"
    )
    
    # Relationship to portfolio stocks
    stocks: List["PortfolioStock"] = Relationship(back_populates="portfolio", cascade_delete=True)


class PortfolioStock(SQLModel, table=True):
    """Portfolio stock model."""
    __tablename__ = "portfolio_stocks"
    
    portfolio_id: UUID = Field(
        foreign_key="portfolio.portfolio_id",
        primary_key=True,
        description="Foreign key to portfolio"
    )
    ticker: str = Field(
        max_length=10,
        primary_key=True,
        description="Stock ticker symbol"
    )
    date_added: datetime = Field(
        default_factory=datetime.now,
        description="When the stock was added to the portfolio"
    )
    
    # Relationship to portfolio
    portfolio: Optional[Portfolio] = Relationship(back_populates="stocks")
