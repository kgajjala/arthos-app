# Arthos

**Richer, Wiser, Happier**

Arthos is a Python web application for investment analysis, built with FastAPI, SQLModel, and yfinance. It provides stock data analysis with technical indicators and caching capabilities.

## Features

- 📊 **Stock Data Analysis**: Fetch and analyze past 365 days of stock data
- 📈 **Technical Indicators**: Calculate 50-day and 200-day Simple Moving Averages (SMA)
- 🎯 **Trading Signals**: Generate trading signals based on standard deviation analysis
- 💾 **Intelligent Caching**: 24-hour cache to reduce API calls to yfinance
- 🧪 **Comprehensive Testing**: Full test coverage with pytest
- 🚀 **FastAPI Backend**: Modern, fast, and async-capable API

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

## API Endpoints

### GET `/v1/stock`

Fetch stock data and compute technical metrics.

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
  "devstep": 1.2345,
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
- `devstep`: Number of standard deviations from 50-day SMA
- `signal`: Trading signal (Neutral, Overbought, Extreme Overbought, Oversold, Extreme Oversold)
- `current_price`: Current stock price
- `data_points`: Number of data points fetched
- `cached`: Boolean indicating if data came from cache
- `cache_timestamp`: ISO timestamp of cache entry (only present when `cached=true`)

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

- `tests/test_api.py` - API endpoint tests
- `tests/test_stock_service.py` - Stock service unit tests
- `tests/test_cache_service.py` - Cache service tests
- `tests/test_stock_service_caching.py` - Caching integration tests

## Project Structure

```
arthos-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py           # Database configuration and setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── stock_cache.py    # StockCache SQLModel
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stock_service.py  # Stock data fetching and metrics
│   │   └── cache_service.py  # Caching operations
│   └── templates/
│       └── index.html        # Homepage template
├── static/
│   └── arthos-favicon.svg    # Favicon
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration and fixtures
│   ├── test_api.py           # API endpoint tests
│   ├── test_stock_service.py  # Stock service tests
│   ├── test_cache_service.py # Cache service tests
│   └── test_stock_service_caching.py  # Caching integration tests
├── run.py                    # Application startup script
├── pytest.ini                # Pytest configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── arthos.db                  # SQLite database (created on first run)
```

## Caching

The application implements intelligent caching to reduce API calls to yfinance:

- **Cache Duration**: 24 hours
- **Automatic Expiration**: Expired cache entries are automatically deleted
- **Cache Storage**: SQLite database (SQLModel)
- **Cache Key**: Stock ticker symbol (case-insensitive)

When a request is made:
1. Check if valid cache exists (not expired)
2. If cache exists, return cached data
3. If cache is missing or expired, fetch from yfinance and cache the response

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
