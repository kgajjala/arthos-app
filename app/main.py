"""FastAPI application for Arthos investment analysis."""
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pathlib import Path
from app.services.stock_service import get_stock_metrics

# Initialize FastAPI app
app = FastAPI(title="Arthos", description="Investment Analysis Platform")

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


@app.get("/v1/stock")
async def get_stock_data(q: str = Query(..., description="Stock ticker symbol")):
    """
    Fetch past 365 days of stock data and compute metrics.
    
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

