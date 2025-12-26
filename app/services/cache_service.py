"""Cache service for stock data."""
from sqlmodel import Session, select
from app.models.stock_cache import StockCache
from app.database import engine
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
import json


CACHE_EXPIRY_HOURS = 24


def get_cached_data(ticker: str) -> Optional[Tuple[pd.DataFrame, datetime]]:
    """
    Get cached stock data for a ticker if it exists and is not expired.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Tuple of (DataFrame, cache_timestamp) if cache exists and is valid, None otherwise
    """
    with Session(engine) as session:
        statement = select(StockCache).where(StockCache.ticker == ticker.upper())
        cache_entry = session.exec(statement).first()
        
        if cache_entry is None:
            return None
        
        # Check if cache is expired (older than 24 hours)
        age = datetime.now() - cache_entry.cache_timestamp
        if age > timedelta(hours=CACHE_EXPIRY_HOURS):
            # Cache expired, delete it
            session.delete(cache_entry)
            session.commit()
            return None
        
        # Deserialize the cached data
        try:
            data_dict = json.loads(cache_entry.data)
            # Convert back to DataFrame - transpose because we stored with orient='index'
            df = pd.DataFrame(data_dict).T
            df.index = pd.to_datetime(df.index)
            return (df, cache_entry.cache_timestamp)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If deserialization fails, delete the corrupted cache entry
            session.delete(cache_entry)
            session.commit()
            return None


def set_cached_data(ticker: str, data: pd.DataFrame) -> None:
    """
    Cache stock data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        data: DataFrame with stock data to cache
    """
    with Session(engine) as session:
        # Convert DataFrame to JSON-serializable format
        data_dict = data.to_dict(orient='index')
        # Convert index (datetime) to string for JSON serialization
        data_dict = {str(k): v for k, v in data_dict.items()}
        data_json = json.dumps(data_dict)
        
        # Check if cache entry already exists
        statement = select(StockCache).where(StockCache.ticker == ticker.upper())
        cache_entry = session.exec(statement).first()
        
        if cache_entry:
            # Update existing entry
            cache_entry.data = data_json
            cache_entry.cache_timestamp = datetime.now()
        else:
            # Create new entry
            cache_entry = StockCache(
                ticker=ticker.upper(),
                data=data_json,
                cache_timestamp=datetime.now()
            )
            session.add(cache_entry)
        
        session.commit()


def purge_expired_cache() -> int:
    """
    Purge all expired cache entries (older than 24 hours).
    
    Returns:
        Number of entries purged
    """
    with Session(engine) as session:
        cutoff_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        statement = select(StockCache).where(StockCache.cache_timestamp < cutoff_time)
        expired_entries = session.exec(statement).all()
        
        count = len(expired_entries)
        for entry in expired_entries:
            session.delete(entry)
        
        session.commit()
        return count

