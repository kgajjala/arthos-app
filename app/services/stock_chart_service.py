"""Service for preparing stock chart data."""
import pandas as pd
from typing import Dict, Any, List
from app.services.stock_service import fetch_stock_data, calculate_sma
from app.services.cache_service import get_cached_data, set_cached_data
from datetime import datetime


def get_stock_chart_data(ticker: str) -> Dict[str, Any]:
    """
    Get stock data formatted for candlestick chart with SMA lines and STD dev bands.
    Fetches 2 years of data but only displays the last 365 days on the chart.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing:
        - ticker: Stock ticker
        - dates: List of date strings (ISO format) - last 365 days
        - candlestick_data: List of dicts with [date, open, high, low, close] - last 365 days
        - sma_50: List of [date, sma_50_value] pairs - last 365 days
        - sma_200: List of [date, sma_200_value] pairs - last 365 days
        - std_bands: Dictionary with std dev bands (1std_upper, 1std_lower, 2std_upper, 2std_lower)
        - current_price: Current stock price
        - sma_50_current: Current 50-day SMA
        - sma_200_current: Current 200-day SMA
        
    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    # Try to get from cache first
    # We need at least 565 days of data (365 for display + 200 for SMA calculation)
    cached_data = get_cached_data(ticker)
    if cached_data:
        data, _ = cached_data
        # Check if cached data has enough days for proper SMA calculations
        # We need at least 565 days (365 display + 200 for SMA 200 calculation)
        if len(data) < 565:
            # Cached data doesn't have enough days, fetch fresh data
            data = fetch_stock_data(ticker)
            # Cache the fetched data
            set_cached_data(ticker, data)
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
    
    # Calculate rolling SMAs and standard deviations for all data
    data['SMA_50'] = data['Close'].rolling(window=50, min_periods=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200, min_periods=200).mean()
    
    # Calculate rolling standard deviation for 50-day window
    data['STD_50'] = data['Close'].rolling(window=50, min_periods=50).std()
    
    # Calculate STD dev bands around SMA 50
    data['SMA_50_plus_1std'] = data['SMA_50'] + data['STD_50']
    data['SMA_50_plus_2std'] = data['SMA_50'] + (2 * data['STD_50'])
    data['SMA_50_minus_1std'] = data['SMA_50'] - data['STD_50']
    data['SMA_50_minus_2std'] = data['SMA_50'] - (2 * data['STD_50'])
    
    # Filter to show data from Jan 1, 2025 onwards (or last 365 days if Jan 1, 2025 is not available)
    # Handle timezone-aware index by normalizing to timezone-naive for comparison
    data_index = data.index
    if data_index.tz is not None:
        # If index is timezone-aware, normalize it for comparison
        data_index_normalized = data_index.tz_localize(None)
        jan_1_2025 = pd.Timestamp('2025-01-01')
        # Filter using normalized index
        mask = data_index_normalized >= jan_1_2025
        data_from_jan_1 = data[mask]
    else:
        # Index is timezone-naive
        jan_1_2025 = pd.Timestamp('2025-01-01')
        data_from_jan_1 = data[data.index >= jan_1_2025]
    
    if len(data_from_jan_1) > 0:
        # We have data from Jan 1, 2025, show up to 365 days from that point
        display_data = data_from_jan_1.head(365)
    else:
        # Jan 1, 2025 data not available (might be future date or no trading day), show last 365 days
        display_data = data.tail(365)
    
    # Prepare candlestick data (last 365 days)
    candlestick_data = []
    dates = []
    
    for date, row in display_data.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        dates.append(date_str)
        candlestick_data.append({
            'x': date_str,
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close'])
        })
    
    # Prepare SMA data (last 365 days)
    sma_50_data = []
    sma_200_data = []
    
    # Prepare STD dev bands data (last 365 days)
    std_1_upper = []
    std_1_lower = []
    std_2_upper = []
    std_2_lower = []
    
    for i, (date, row) in enumerate(display_data.iterrows()):
        date_str = date.strftime('%Y-%m-%d')
        
        # SMA values
        sma_50 = float(row['SMA_50']) if pd.notna(row['SMA_50']) else None
        sma_200 = float(row['SMA_200']) if pd.notna(row['SMA_200']) else None
        
        sma_50_data.append({
            'x': date_str,
            'y': sma_50
        })
        sma_200_data.append({
            'x': date_str,
            'y': sma_200
        })
        
        # STD dev bands (only if SMA_50 is available)
        if pd.notna(row['SMA_50']):
            std_1_upper.append({
                'x': date_str,
                'y': float(row['SMA_50_plus_1std']) if pd.notna(row['SMA_50_plus_1std']) else None
            })
            std_1_lower.append({
                'x': date_str,
                'y': float(row['SMA_50_minus_1std']) if pd.notna(row['SMA_50_minus_1std']) else None
            })
            std_2_upper.append({
                'x': date_str,
                'y': float(row['SMA_50_plus_2std']) if pd.notna(row['SMA_50_plus_2std']) else None
            })
            std_2_lower.append({
                'x': date_str,
                'y': float(row['SMA_50_minus_2std']) if pd.notna(row['SMA_50_minus_2std']) else None
            })
        else:
            std_1_upper.append({'x': date_str, 'y': None})
            std_1_lower.append({'x': date_str, 'y': None})
            std_2_upper.append({'x': date_str, 'y': None})
            std_2_lower.append({'x': date_str, 'y': None})
    
    # Get current values (from full dataset)
    current_price = float(data['Close'].iloc[-1])
    sma_50_current = calculate_sma(data, 50)
    sma_200_current = calculate_sma(data, 200)
    
    return {
        "ticker": ticker.upper(),
        "dates": dates,
        "candlestick_data": candlestick_data,
        "sma_50": sma_50_data,
        "sma_200": sma_200_data,
        "std_bands": {
            "std_1_upper": std_1_upper,
            "std_1_lower": std_1_lower,
            "std_2_upper": std_2_upper,
            "std_2_lower": std_2_lower
        },
        "current_price": round(current_price, 2),
        "sma_50_current": round(sma_50_current, 2),
        "sma_200_current": round(sma_200_current, 2)
    }

