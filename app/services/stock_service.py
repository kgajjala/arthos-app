"""Stock data fetching and metric calculation service."""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from app.services.cache_service import get_cached_data, set_cached_data


def fetch_stock_data(ticker: str) -> pd.DataFrame:
    """
    Fetch past 365 days of stock data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        DataFrame with stock data including 'Close' prices
        
    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch past 1 year of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
            
        return hist
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")


def calculate_sma(data: pd.DataFrame, window: int) -> float:
    """
    Calculate Simple Moving Average (SMA) for the given window.
    
    Args:
        data: DataFrame with 'Close' prices
        window: Number of days for the moving average
        
    Returns:
        SMA value
    """
    if len(data) < window:
        # If not enough data, use available data
        window = len(data)
    return data['Close'].tail(window).mean()


def calculate_devstep(data: pd.DataFrame, sma_50: float) -> float:
    """
    Calculate the number of standard deviations the current price is from the 50-day SMA.
    
    Args:
        data: DataFrame with 'Close' prices
        sma_50: 50-day Simple Moving Average
        
    Returns:
        Number of standard deviations (devstep)
    """
    if len(data) < 50:
        # Use available data if less than 50 days
        window = len(data)
    else:
        window = 50
    
    recent_prices = data['Close'].tail(window)
    current_price = data['Close'].iloc[-1]
    std_dev = recent_prices.std()
    
    if std_dev == 0:
        return 0.0
    
    devstep = (current_price - sma_50) / std_dev
    return devstep


def calculate_signal(devstep: float) -> str:
    """
    Calculate trading signal based on devstep value.
    
    Args:
        devstep: Number of standard deviations from 50-day SMA
        
    Returns:
        Signal string: 'Neutral', 'Overbought', 'Extreme Overbought', 
                       'Oversold', or 'Extreme Oversold'
    """
    if devstep < -2:
        return "Extreme Oversold"
    elif devstep < -1:
        return "Oversold"
    elif devstep <= 1:
        return "Neutral"
    elif devstep <= 2:
        return "Overbought"
    else:
        return "Extreme Overbought"


def get_stock_metrics(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock data and calculate all required metrics.
    Uses cache if available and not expired (24 hours).
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing:
        - ticker: Stock ticker
        - sma_50: 50-day Simple Moving Average
        - sma_200: 200-day Simple Moving Average
        - devstep: Number of standard deviations from 50-day SMA
        - signal: Trading signal
        - current_price: Current stock price
        - data_points: Number of data points fetched
        - cached: Boolean indicating if data came from cache
        - cache_timestamp: ISO timestamp of cache entry (if cached)
    """
    cached_result = None
    cache_timestamp = None
    
    # Try to get from cache first
    cached_data = get_cached_data(ticker)
    if cached_data:
        data, cache_timestamp = cached_data
        cached_result = True
    else:
        # Fetch from yfinance
        data = fetch_stock_data(ticker)
        # Cache the fetched data
        set_cached_data(ticker, data)
        cached_result = False
    
    # Calculate SMAs
    sma_50 = calculate_sma(data, 50)
    sma_200 = calculate_sma(data, 200)
    
    # Calculate devstep
    devstep = calculate_devstep(data, sma_50)
    
    # Calculate signal
    signal = calculate_signal(devstep)
    
    # Get current price
    current_price = float(data['Close'].iloc[-1])
    
    result = {
        "ticker": ticker.upper(),
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "devstep": round(devstep, 4),
        "signal": signal,
        "current_price": round(current_price, 2),
        "data_points": len(data),
        "cached": cached_result
    }
    
    # Add cache_timestamp only if data was cached
    if cached_result and cache_timestamp:
        result["cache_timestamp"] = cache_timestamp.isoformat()
    
    return result

