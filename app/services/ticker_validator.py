"""Ticker validation service."""
import re
from typing import List, Tuple


def validate_ticker_format(ticker: str) -> bool:
    """
    Validate ticker format (basic format check).
    
    Stock tickers are typically:
    - 1-5 characters
    - Alphanumeric (letters and numbers)
    - May contain dots (for some exchanges)
    
    Args:
        ticker: Stock ticker symbol to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    if not ticker or not ticker.strip():
        return False
    
    ticker = ticker.strip().upper()
    
    # Basic format: 1-5 characters, alphanumeric, may contain dots
    # Examples: AAPL, MSFT, BRK.B, GOOGL
    pattern = r'^[A-Z0-9]{1,5}(\.[A-Z0-9]{1,5})?$'
    
    return bool(re.match(pattern, ticker))


def validate_ticker_list(tickers: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of tickers and separate valid from invalid.
    
    Args:
        tickers: List of ticker symbols to validate
        
    Returns:
        Tuple of (valid_tickers, invalid_tickers)
    """
    valid = []
    invalid = []
    
    for ticker in tickers:
        ticker = ticker.strip().upper()
        if not ticker:
            continue
        
        if validate_ticker_format(ticker):
            valid.append(ticker)
        else:
            invalid.append(ticker)
    
    return valid, invalid

