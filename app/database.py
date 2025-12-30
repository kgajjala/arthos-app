"""Database configuration using SQLModel."""
from sqlmodel import SQLModel, create_engine, Session
from app.models.stock_cache import StockCache  # Import to register with metadata
from app.models.fmp_cache import FMPCache  # Import to register with metadata

# Database URL - using SQLite for now, can be easily swapped for Postgres later
DATABASE_URL = "sqlite:///arthos.db"

# Create engine - separated for easy swapping to Postgres
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session

