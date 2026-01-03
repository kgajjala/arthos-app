# Arthos

**Richer, Wiser, Happier**

Arthos is a Python web application for investment analysis, built with FastAPI, SQLModel, and yfinance. It provides stock data analysis with technical indicators and caching capabilities.

## Features

- 📊 **Stock Data Analysis**: Fetch and analyze stock data (2 years fetched, 365 days displayed)
- 📈 **Technical Indicators**: Calculate 50-day and 200-day Simple Moving Averages (SMA)
- 🎯 **Trading Signals**: Generate trading signals based on standard deviation analysis
- 📉 **Interactive Charts**: Candlestick charts with SMA overlays for detailed stock analysis
- 💾 **Intelligent Caching**: 60-minute cache to reduce API calls to yfinance
- 📁 **Portfolio Management**: Create and manage stock portfolios with multiple stocks
- ✏️ **Portfolio Editing**: Edit portfolio names and manage stocks within portfolios
- 🔗 **Stock Detail Pages**: Click any ticker to view detailed charts and metrics
- 🧪 **Comprehensive Testing**: Full test coverage with pytest (unit, API, and browser tests)
- 🚀 **FastAPI Backend**: Modern, fast, and async-capable API

## Screenshots

### Homepage
![Homepage](docs/screenshots/homepage.png)

The homepage allows you to enter stock tickers and explore their metrics.

### Results Page
![Results Page](docs/screenshots/results-page.png)

View comprehensive stock metrics in a sortable, searchable table with custom signal sorting.

### Stock Detail Page
![Stock Detail Page](docs/screenshots/stock-detail.png)

Interactive candlestick chart with 50-day and 200-day SMAs, plus standard deviation bands for detailed analysis.

### Portfolio Management
![Portfolios List](docs/screenshots/portfolios-list.png)

View all your portfolios in one place.

![Create Portfolio](docs/screenshots/create-portfolio.png)

Create new portfolios with a simple form.

![Portfolio Details](docs/screenshots/portfolio-details.png)

Manage stocks within a portfolio, view metrics, and add or remove stocks.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (tested with Python 3.9.6)
- **pip** (Python package installer)
- **git** (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kgajjala/arthos-app.git
cd arthos-app
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 4. Initialize the Database

The database will be automatically created and initialized when you first run the application. The SQLite database file (`arthos.db`) will be created in the project root directory.

## Running the Application

### Start the Development Server

```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

### Access the Homepage

Open your browser and navigate to:
```
http://localhost:8000
```

### Portfolio Management Pages

- **Create Portfolio**: http://localhost:8000/create-portfolio
- **List All Portfolios**: http://localhost:8000/portfolios
- **Portfolio Details**: http://localhost:8000/portfolio/{portfolio_id}

### Stock Detail Page

- **Stock Details**: http://localhost:8000/stock/{ticker}
  - Interactive candlestick chart showing 365 days of price data
  - 50-day and 200-day SMA lines overlaid on the chart
  - Current metrics display panel
  - Accessible by clicking any ticker symbol in results or portfolio tables

## API Endpoints

### GET `/v1/stock`

Fetch stock data and compute technical metrics using yfinance.

**Query Parameters:**
- `q` (required): Stock ticker symbol (e.g., `AAPL`, `MSFT`, `GOOGL`)

**Example Request:**
```bash
curl "http://localhost:8000/v1/stock?q=AAPL"
```

**Example Response:**
```json
{
  "ticker": "AAPL",
  "sma_50": 150.25,
  "sma_200": 145.80,
  "devstep": 1.2345,  # 50D STDDEV
  "signal": "Overbought",
  "current_price": 155.50,
  "data_points": 252,
  "cached": false,
  "cache_timestamp": "2025-12-25T21:44:22.981176"
}
```

**Response Fields:**
- `ticker`: Stock ticker symbol (uppercase)
- `sma_50`: 50-day Simple Moving Average
- `sma_200`: 200-day Simple Moving Average
- `devstep`: Number of standard deviations from 50-day SMA (displayed as "50D STDDEV")
- `signal`: Trading signal (Neutral, Overbought, Extreme Overbought, Oversold, Extreme Oversold)
- `current_price`: Current stock price
- `data_points`: Number of data points fetched
- `cached`: Boolean indicating if data came from cache
- `cache_timestamp`: ISO timestamp of cache entry (only present when `cached=true`)

### GET `/results`

Display stock metrics results page for multiple tickers.

**Query Parameters:**
- `tickers` (required): Comma-separated list of stock ticker symbols (e.g., `AAPL,MSFT,GOOGL`)

**Example Request:**
```bash
curl "http://localhost:8000/results?tickers=AAPL,MSFT"
```

Returns an HTML page with a DataTable showing metrics for all requested tickers.

### GET `/validate/tickers`

Validate ticker format for a list of tickers.

**Query Parameters:**
- `tickers` (required): Comma-separated list of stock ticker symbols

**Example Request:**
```bash
curl "http://localhost:8000/validate/tickers?tickers=AAPL,MSFT,INVALID123"
```

**Example Response:**
```json
{
  "valid": ["AAPL", "MSFT"],
  "invalid": [
    {
      "ticker": "INVALID123",
      "error": "Invalid format. Tickers must be 1-5 alphanumeric characters."
    }
  ]
}
```

### GET `/stock/{ticker}`

Display stock detail page with interactive candlestick chart.

**Path Parameters:**
- `ticker` (required): Stock ticker symbol (e.g., `AAPL`, `MSFT`)

**Example Request:**
```bash
curl "http://localhost:8000/stock/AAPL"
```

Returns an HTML page with:
- Interactive Plotly.js candlestick chart showing 365 days of price data
- 50-day and 200-day SMA lines overlaid on the chart
- Current metrics panel with price, SMAs, 50D STDDEV, and signal

## Portfolio API Endpoints

### GET `/v1/portfolio`

List all portfolios.

**Example Request:**
```bash
curl "http://localhost:8000/v1/portfolio"
```

**Example Response:**
```json
{
  "portfolios": [
    {
      "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
      "portfolio_name": "My Portfolio",
      "date_added": "2025-12-25T21:44:22.981176",
      "date_modified": "2025-12-25T21:44:22.981176"
    }
  ]
}
```

### GET `/v1/portfolio/{portfolio_id}`

Get portfolio details including all stocks.

**Example Request:**
```bash
curl "http://localhost:8000/v1/portfolio/550e8400-e29b-41d4-a716-446655440000"
```

**Example Response:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "portfolio_name": "My Portfolio",
  "date_added": "2025-12-25T21:44:22.981176",
  "date_modified": "2025-12-25T21:44:22.981176",
  "stocks": [
    {
      "ticker": "AAPL",
      "date_added": "2025-12-25T21:45:00.000000"
    }
  ]
}
```

### POST `/v1/portfolio`

Create a new portfolio.

**Request Body:**
```json
{
  "portfolio_name": "My New Portfolio"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/v1/portfolio" \
  -H "Content-Type: application/json" \
  -d '{"portfolio_name": "My New Portfolio"}'
```

### PUT `/v1/portfolio/{portfolio_id}`

Update portfolio name.

**Request Body:**
```json
{
  "portfolio_name": "Updated Portfolio Name"
}
```

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/v1/portfolio/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"portfolio_name": "Updated Portfolio Name"}'
```

### DELETE `/v1/portfolio/{portfolio_id}`

Delete a portfolio and all its stocks (cascade delete).

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/v1/portfolio/550e8400-e29b-41d4-a716-446655440000"
```

### POST `/v1/portfolio/{portfolio_id}/stocks`

Add stocks to a portfolio. Duplicate stocks are automatically ignored.

**Request Body:**
```json
{
  "tickers": "AAPL,MSFT,GOOGL"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/v1/portfolio/550e8400-e29b-41d4-a716-446655440000/stocks" \
  -H "Content-Type: application/json" \
  -d '{"tickers": "AAPL,MSFT,GOOGL"}'
```

### DELETE `/v1/portfolio/{portfolio_id}/stocks/{ticker}`

Remove a stock from a portfolio.

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/v1/portfolio/550e8400-e29b-41d4-a716-446655440000/stocks/AAPL"
```

## Testing

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_stock_service.py -v

# Run with coverage (if pytest-cov is installed)
pytest --cov=app --cov-report=html
```

### Test Structure

- `tests/test_api.py` - Stock API endpoint tests
- `tests/test_stock_service.py` - Stock service unit tests
- `tests/test_cache_service.py` - Cache service tests
- `tests/test_stock_service_caching.py` - Caching integration tests
- `tests/test_ticker_validator.py` - Ticker validation tests
- `tests/test_validation_api.py` - Validation API endpoint tests
- `tests/test_results_page.py` - Results page tests
- `tests/test_portfolio_models.py` - Portfolio model tests
- `tests/test_portfolio_service.py` - Portfolio service unit tests
- `tests/test_portfolio_api.py` - Portfolio API endpoint tests
- `tests/test_portfolio_browser.py` - Portfolio browser tests (Playwright)
- `tests/test_stock_chart_service.py` - Stock chart service tests
- `tests/test_stock_detail_api.py` - Stock detail page API tests

## Project Structure

```
arthos-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py           # Database configuration and setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── stock_cache.py    # StockCache SQLModel
│   │   └── portfolio.py      # Portfolio and PortfolioStock SQLModels
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stock_service.py  # Stock data fetching and metrics
│   │   ├── stock_chart_service.py  # Stock chart data preparation
│   │   ├── cache_service.py  # Caching operations
│   │   ├── ticker_validator.py  # Ticker format validation
│   │   └── portfolio_service.py  # Portfolio management operations
│   └── templates/
│       ├── index.html        # Homepage template
│       ├── results.html      # Results page template
│       ├── stock_detail.html  # Stock detail page with chart
│       ├── create_portfolio.html  # Create portfolio page
│       ├── portfolios.html    # List portfolios page
│       └── portfolio_details.html  # Portfolio details page
├── static/
│   └── arthos-favicon.svg    # Favicon
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration and fixtures
│   ├── test_api.py           # Stock API endpoint tests
│   ├── test_stock_service.py  # Stock service tests
│   ├── test_cache_service.py # Cache service tests
│   ├── test_stock_service_caching.py  # Caching integration tests
│   ├── test_ticker_validator.py  # Ticker validation tests
│   ├── test_validation_api.py  # Validation API endpoint tests
│   ├── test_results_page.py  # Results page tests
│   ├── test_portfolio_models.py  # Portfolio model tests
│   ├── test_portfolio_service.py  # Portfolio service tests
│   ├── test_portfolio_api.py  # Portfolio API endpoint tests
│   └── test_portfolio_browser.py  # Portfolio browser tests (Playwright)
├── run.py                    # Application startup script
├── pytest.ini                # Pytest configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── arthos.db                  # SQLite database (created on first run)
```

## Caching

The application implements intelligent caching to reduce API calls to yfinance:

- **Cache Duration**: 60 minutes
- **Automatic Expiration**: Expired cache entries are automatically deleted
- **Cache Storage**: SQLite database (SQLModel)
- **Cache Key**: Stock ticker symbol (case-insensitive)

When a request is made:
1. Check if valid cache exists (not expired)
2. If cache exists, return cached data
3. If cache is missing or expired, fetch from yfinance and cache the response

## Portfolio Management

The application includes a comprehensive portfolio management system:

### Features

- **Create Portfolios**: Create named portfolios to organize your stock analysis
- **Add Stocks**: Add multiple stocks to a portfolio using comma-separated tickers
- **Edit Portfolio Names**: Update portfolio names after creation
- **Remove Stocks**: Delete individual stocks from portfolios
- **View Portfolio Details**: See all stocks in a portfolio with their current metrics
- **Cascade Delete**: Deleting a portfolio automatically removes all associated stocks
- **Duplicate Prevention**: Adding the same stock twice to a portfolio is automatically ignored

### Portfolio Name Validation

- Alphanumeric characters and spaces only
- Maximum 128 characters
- Names are automatically trimmed of leading/trailing whitespace

### Stock Management

- Stocks are validated using the same ticker validation rules as the main search
- Each portfolio can contain unique stocks only (no duplicates)
- Stock metrics are displayed in a DataTable with the same columns as the results page
- Custom sorting by Signal column (Extreme Oversold → Extreme Overbought)

## Stock Detail Pages

Each stock has a dedicated detail page accessible by clicking the ticker symbol in any table:

### Features

- **Interactive Candlestick Chart**: Plotly.js-powered chart showing 365 days of daily price data
- **SMA Overlays**: 50-day and 200-day Simple Moving Averages displayed as lines on the chart
- **Standard Deviation Bands**: Color-coded shaded areas showing standard deviation bands around the 50-day SMA
- **Current Metrics Panel**: Sidebar showing current price, SMAs, 50D STDDEV, and signal
- **Responsive Design**: Chart and metrics adapt to different screen sizes
- **Color-Coded Signals**: Visual badges matching the signal classification system

### Chart Features

- **Candlestick Visualization**: Green candles for price increases, red for decreases
- **Standard Deviation Bands**: Color-coded bands showing price zones:
  - **Gray**: Neutral zone (-1 to +1 STD)
  - **Light Red/Pink**: Moderate overbought zone (+1 to +2 STD)
  - **Darker Red**: Extreme overbought zone (+2 to +3 STD)
  - **Slightly Darker Green**: Moderate oversold zone (-1 to -2 STD)
  - **Light Green**: Extreme oversold zone (-2 to -3 STD)
- **Interactive Tooltips**: Hover over any point to see detailed price information
- **Zoom and Pan**: Built-in Plotly.js controls for exploring the data
- **Date Range**: Displays the past 365 days of trading data (fetches 2 years to enable proper SMA calculations)

## Development

### Code Style

The project follows Python best practices. Consider using:
- **Black** for code formatting
- **flake8** or **pylint** for linting
- **mypy** for type checking

### Database Migrations

Currently using SQLite. To migrate to PostgreSQL:

1. Update `DATABASE_URL` in `app/database.py`:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost/arthos"
   ```

2. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. The SQLModel models will work with PostgreSQL without changes.

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError` when running the app
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database errors on first run
- **Solution**: The database is created automatically. Ensure write permissions in the project directory

**Issue**: yfinance API errors
- **Solution**: Check internet connection. Some tickers may not be available or may require authentication

**Issue**: Port 8000 already in use
- **Solution**: Change the port in `run.py` or use: `uvicorn app.main:app --port 8001`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the Arthos investment analysis platform.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, SQLModel, and yfinance**
