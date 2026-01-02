"""Live browser test for results page sorting - requires server to be running."""
import pytest
from playwright.sync_api import sync_playwright, Page, expect
import time


@pytest.mark.skip(reason="Requires server to be running on localhost:8000")
def test_results_page_signal_sorting_live():
    """Test sorting by starting a real browser and navigating to the results page.
    
    To run this test:
    1. Start the server: python run.py
    2. Run: pytest tests/test_results_sorting_live.py -v -s
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see the browser
        page = browser.new_page()
        
        # Navigate to results page with multiple tickers
        page.goto("http://localhost:8000/results?tickers=AAPL,MSFT,GOOGL,TSLA,AMZN")
        
        # Wait for table to load and DataTable to initialize
        page.wait_for_selector('#metricsTable', state='visible')
        page.wait_for_timeout(3000)  # Give DataTable time to initialize and sort
        
        # Get all signal values from the table
        signal_cells = page.locator('#metricsTable tbody tr td:nth-child(6)')
        
        # Extract signal text from badges
        signals = []
        count = signal_cells.count()
        print(f"\nFound {count} rows in table")
        
        for i in range(count):
            cell = signal_cells.nth(i)
            # Try to get badge text first, fallback to cell text
            badge = cell.locator('.badge')
            if badge.count() > 0:
                signal_text = badge.inner_text()
            else:
                signal_text = cell.inner_text()
            signals.append(signal_text.strip())
            print(f"Row {i+1}: {signal_text.strip()}")
        
        # Expected order: Extreme Oversold (5) > Oversold (4) > Neutral (3) > Overbought (2) > Extreme Overbought (1)
        priority_map = {
            'Extreme Oversold': 5,
            'Oversold': 4,
            'Neutral': 3,
            'Overbought': 2,
            'Extreme Overbought': 1
        }
        
        # Print the order
        print("\nSignal order (should be descending priority):")
        for i, signal in enumerate(signals):
            priority = priority_map.get(signal, 0)
            print(f"  {i+1}. {signal} (priority: {priority})")
        
        # Verify signals are in descending priority order
        if len(signals) > 1:
            errors = []
            for i in range(len(signals) - 1):
                current_priority = priority_map.get(signals[i], 0)
                next_priority = priority_map.get(signals[i + 1], 0)
                if current_priority < next_priority:
                    errors.append(
                        f"Row {i+1}: {signals[i]} (priority {current_priority}) should come before "
                        f"{signals[i + 1]} (priority {next_priority})"
                    )
            
            if errors:
                print("\n❌ Sorting errors found:")
                for error in errors:
                    print(f"  - {error}")
                assert False, "Sorting is incorrect. See errors above."
            else:
                print("\n✅ Sorting is correct!")
        
        browser.close()


if __name__ == "__main__":
    # Allow running this test directly
    test_results_page_signal_sorting_live()

