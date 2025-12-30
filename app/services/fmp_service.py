"""FMP (Financial Modeling Prep) API service for stock data."""
import requests
import pandas as pd
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from app.config import FMP_API_KEY, FMP_API_BASE_URL
from app.services.fmp_cache_service import get_fmp_cached_data, set_fmp_cached_data
from app.services.stock_service import calculate_sma, calculate_devstep, calculate_signal

# Set up logger for FMP API (ERROR level only - no request/response logging)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def fetch_fmp_stock_data(ticker: str) -> pd.DataFrame:
    """
    Fetch past 365 days of stock data for a given ticker from FMP API.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        DataFrame with stock data including 'Close' prices
        
    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
        requests.RequestException: If API request fails
    """
    if not FMP_API_KEY or FMP_API_KEY == "***MASKED***":
        raise ValueError("FMP API key is not configured. Set FMP_API_KEY environment variable.")
    
    try:
        # Calculate date range (1 year ago to today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # FMP API endpoint for historical data (using stable API as per documentation)
        # Endpoint: /historical-price-eod/full?symbol={symbol}
        url = f"{FMP_API_BASE_URL}/historical-price-eod/full"
        params = {
            "symbol": ticker,
            "apikey": FMP_API_KEY,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d")
        }
        
        # Log request details (mask API key for security)
        logger.info(f"[FMP API] Request for ticker: {ticker}")
        logger.info(f"[FMP API] URL: {url}")
        logger.info(f"[FMP API] Params: symbol={ticker}, from={params['from']}, to={params['to']}, apikey=***MASKED***")
        
        response = requests.get(url, params=params, timeout=30)
        
        # Log response status
        logger.info(f"[FMP API] Response Status: {response.status_code} {response.reason}")
        
        # Handle rate limiting (429) and other errors
        if response.status_code == 429:
            logger.error(f"[FMP API] Rate limit exceeded (429)")
            raise ValueError("FMP API rate limit exceeded. Please try again later.")
        elif response.status_code == 403:
            logger.error(f"[FMP API] Invalid or missing API key (403)")
            raise ValueError("FMP API key is invalid or missing. Please check your API key.")
        elif response.status_code == 500:
            logger.error(f"[FMP API] Internal server error (500)")
            raise ValueError("FMP API internal server error. Please try again later.")
        
        response.raise_for_status()  # Raises an HTTPError for other bad responses
        
        data = response.json()
        
        # Log response summary
        logger.info(f"[FMP API] Response data type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        
        # Check if response is a list (new API format) or dict (old format)
        if isinstance(data, list):
            # New API format: returns list of historical data directly
            if not data:
                logger.warning(f"[FMP API] Empty list returned for ticker: {ticker}")
                raise ValueError(f"No historical data found for ticker: {ticker}")
            logger.info(f"[FMP API] Response: Success - {len(data)} historical data points received")
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Old format or error response
            if "Error Message" in data:
                error_msg = data['Error Message']
                logger.error(f"[FMP API] Error Message: {error_msg}")
                raise ValueError(f"FMP API error: {error_msg}")
            
            if "historical" in data and data["historical"]:
                logger.info(f"[FMP API] Response: Success - {len(data['historical'])} historical data points received")
                df = pd.DataFrame(data["historical"])
            else:
                logger.warning(f"[FMP API] No historical data found for ticker: {ticker}")
                raise ValueError(f"No historical data found for ticker: {ticker}")
        else:
            logger.error(f"[FMP API] Unexpected response format: {type(data)}")
            raise ValueError(f"Unexpected FMP API response format for ticker: {ticker}")
        
        # Log column names for debugging
        logger.info(f"[FMP API] DataFrame columns: {list(df.columns)}")
        
        # Rename columns to match expected format (handle both lowercase and mixed case)
        # Map common column name variations
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ["date", "datetime"]:
                column_mapping[col] = "Date"
            elif col_lower == "close":
                column_mapping[col] = "Close"
            elif col_lower == "open":
                column_mapping[col] = "Open"
            elif col_lower == "high":
                column_mapping[col] = "High"
            elif col_lower == "low":
                column_mapping[col] = "Low"
            elif col_lower == "volume":
                column_mapping[col] = "Volume"
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            logger.info(f"[FMP API] Renamed columns: {column_mapping}")
        
        # Convert date column to datetime and set as index
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        else:
            # Try to find date-like column
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
                df = df.set_index(date_cols[0])
                logger.info(f"[FMP API] Using '{date_cols[0]}' as date index")
            else:
                logger.warning(f"[FMP API] No date column found, using default index")
        
        # Sort by date (ascending)
        df = df.sort_index()
        
        # Ensure we have Close column
        if "Close" not in df.columns:
            raise ValueError(f"Close price data not found for ticker: {ticker}")
        
        if df.empty:
            logger.warning(f"[FMP API] DataFrame is empty after processing for ticker: {ticker}")
            raise ValueError(f"No data found for ticker: {ticker}")
        
        logger.info(f"[FMP API] Successfully processed data for {ticker}: {len(df)} rows, date range {df.index.min()} to {df.index.max()}")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[FMP API] Request exception for {ticker}: {str(e)}")
        raise ValueError(f"FMP API request failed for {ticker}: {str(e)}")
    except KeyError as e:
        logger.error(f"[FMP API] KeyError for {ticker}: {str(e)}")
        raise ValueError(f"Unexpected FMP API response format for {ticker}: {str(e)}")
    except Exception as e:
        logger.error(f"[FMP API] Unexpected error for {ticker}: {str(e)}")
        raise ValueError(f"Error fetching FMP data for {ticker}: {str(e)}")


def get_fmp_stock_metrics(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock data from FMP API and calculate all required metrics.
    Uses cache if available and not expired (24 hours).
    Always uses cache if available and not expired, even if API fails.
    
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
    cached_data = get_fmp_cached_data(ticker)
    if cached_data:
        data, cache_timestamp = cached_data
        cached_result = True
        logger.info(f"[FMP API] Using cached data for {ticker} (cached at {cache_timestamp})")
    else:
        # Fetch from FMP API
        logger.info(f"[FMP API] Cache miss for {ticker}, fetching from API...")
        try:
            data = fetch_fmp_stock_data(ticker)
            # Cache the fetched data
            set_fmp_cached_data(ticker, data)
            cached_result = False
            logger.info(f"[FMP API] Successfully fetched and cached data for {ticker}")
        except Exception as e:
            # If API fails and no cache, raise the error
            logger.error(f"[FMP API] Failed to fetch data for {ticker} and no cache available: {str(e)}")
            raise ValueError(f"Failed to fetch data and no cache available: {str(e)}")
    
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


def get_fmp_multiple_stock_metrics(tickers: list) -> list:
    """
    Fetch stock metrics for multiple tickers using FMP API.
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        List of dictionaries containing metrics for each ticker.
        Failed tickers will have an 'error' field instead of metrics.
    """
    results = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        if not ticker:
            continue
        
        try:
            metrics = get_fmp_stock_metrics(ticker)
            results.append(metrics)
        except Exception as e:
            # Add error entry for failed ticker
            results.append({
                "ticker": ticker,
                "error": str(e)
            })
    
    return results

