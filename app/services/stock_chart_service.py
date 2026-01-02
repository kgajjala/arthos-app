"""Service for preparing stock chart data."""
import pandas as pd
from typing import Dict, Any, List
from app.services.stock_service import fetch_stock_data, calculate_sma
from app.services.cache_service import get_cached_data, set_cached_data
from datetime import datetime


def get_stock_chart_data(ticker: str) -> Dict[str, Any]:
    """
    Get stock data formatted for candlestick chart with SMA lines.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing:
        - ticker: Stock ticker
        - dates: List of date strings (ISO format)
        - candlestick_data: List of dicts with [date, open, high, low, close]
        - sma_50: List of [date, sma_50_value] pairs (None for days without enough data)
        - sma_200: List of [date, sma_200_value] pairs (None for days without enough data)
        - current_price: Current stock price
        - sma_50_current: Current 50-day SMA
        - sma_200_current: Current 200-day SMA
        
    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    # Try to get from cache first
    cached_data = get_cached_data(ticker)
    if cached_data:
        data, _ = cached_data
    else:
        # Fetch from yfinance
        data = fetch_stock_data(ticker)
        # Cache the fetched data
        set_cached_data(ticker, data)
    
    # Ensure we have the required columns
    if not all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
        raise ValueError(f"Incomplete data for ticker: {ticker}")
    
    # Sort by date to ensure chronological order
    data = data.sort_index()
    
    # Prepare candlestick data
    candlestick_data = []
    dates = []
    
    for date, row in data.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        dates.append(date_str)
        candlestick_data.append({
            'x': date_str,
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close'])
        })
    
    # Calculate rolling SMAs for each day
    sma_50_data = []
    sma_200_data = []
    
    # Calculate rolling SMAs using pandas rolling window
    data['SMA_50'] = data['Close'].rolling(window=50, min_periods=1).mean()
    data['SMA_200'] = data['Close'].rolling(window=200, min_periods=1).mean()
    
    for i in range(len(data)):
        date_str = dates[i]
        row = data.iloc[i]
        
        # Get SMA values (None if not enough data for proper calculation)
        sma_50 = float(row['SMA_50']) if pd.notna(row['SMA_50']) else None
        sma_200 = float(row['SMA_200']) if pd.notna(row['SMA_200']) else None
        
        # Only show SMA if we have enough data points for meaningful calculation
        if i < 49:  # Need at least 50 days for SMA 50
            sma_50 = None
        if i < 199:  # Need at least 200 days for SMA 200
            sma_200 = None
        
        sma_50_data.append({
            'x': date_str,
            'y': sma_50
        })
        sma_200_data.append({
            'x': date_str,
            'y': sma_200
        })
    
    # Get current values
    current_price = float(data['Close'].iloc[-1])
    sma_50_current = calculate_sma(data, 50)
    sma_200_current = calculate_sma(data, 200)
    
    return {
        "ticker": ticker.upper(),
        "dates": dates,
        "candlestick_data": candlestick_data,
        "sma_50": sma_50_data,
        "sma_200": sma_200_data,
        "current_price": round(current_price, 2),
        "sma_50_current": round(sma_50_current, 2),
        "sma_200_current": round(sma_200_current, 2)
    }

