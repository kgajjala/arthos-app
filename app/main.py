"""FastAPI application for Arthos investment analysis."""
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pathlib import Path
from app.services.stock_service import get_stock_metrics
from app.database import create_db_and_tables

# Initialize FastAPI app
app = FastAPI(title="Arthos", description="Investment Analysis Platform")

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    create_db_and_tables()

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files (for CSS, JS, images, etc.)
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def home(request: Request):
    """Homepage route."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/results")
async def results(request: Request, tickers: str = Query(..., description="Comma-separated stock tickers")):
    """
    Display stock metrics results page.
    
    Args:
        tickers: Comma-separated list of stock ticker symbols
        
    Returns:
        HTML page with stock metrics in a DataTable
    """
    from app.services.stock_service import get_multiple_stock_metrics
    
    if not tickers or not tickers.strip():
        raise HTTPException(status_code=400, detail="At least one ticker symbol is required")
    
    # Parse tickers
    ticker_list = [t.strip().upper() for t in tickers.split(',') if t.strip()]
    
    if not ticker_list:
        raise HTTPException(status_code=400, detail="At least one valid ticker symbol is required")
    
    # Fetch metrics for all tickers
    try:
        metrics_list = get_multiple_stock_metrics(ticker_list)
        # Format numbers for display
        for metric in metrics_list:
            if 'error' not in metric:
                metric['current_price_formatted'] = f"${metric['current_price']:.2f}"
                metric['sma_50_formatted'] = f"${metric['sma_50']:.2f}"
                metric['sma_200_formatted'] = f"${metric['sma_200']:.2f}"
                metric['devstep_formatted'] = f"{metric['devstep']:.4f}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "metrics": metrics_list,
        "tickers": ticker_list
    })


@app.get("/v1/stock")
async def get_stock_data(q: str = Query(..., description="Stock ticker symbol")):
    """
    Fetch past 365 days of stock data and compute metrics.
    Uses caching to avoid unnecessary yfinance API calls (24-hour cache).
    
    Args:
        q: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        JSON response with stock metrics:
        - ticker: Stock ticker
        - sma_50: 50-day Simple Moving Average
        - sma_200: 200-day Simple Moving Average
        - devstep: Number of standard deviations from 50-day SMA
        - signal: Trading signal (Neutral, Overbought, etc.)
        - current_price: Current stock price
        - data_points: Number of data points fetched
        - cached: Boolean indicating if data came from cache
        - cache_timestamp: ISO timestamp of cache entry (only if cached=true)
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Ticker symbol (q) is required")
    
    try:
        metrics = get_stock_metrics(q.strip().upper())
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

