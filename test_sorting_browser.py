#!/usr/bin/env python3
"""Simple script to test sorting in a browser using Playwright.
Run this while the server is running on localhost:8000"""
from playwright.sync_api import sync_playwright
import time


def test_sorting():
    """Test the results page sorting in a real browser."""
    with sync_playwright() as p:
        # Launch browser (set headless=False to see it)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navigating to results page...")
        page.goto("http://localhost:8000/results?tickers=AAPL,MSFT,GOOGL,TSLA,AMZN")
        
        # Wait for table to load
        print("Waiting for table to load...")
        page.wait_for_selector('#metricsTable', state='visible')
        time.sleep(3)  # Give DataTable time to initialize and sort
        
        # Get all signal values
        signal_cells = page.locator('#metricsTable tbody tr td:nth-child(6)')
        count = signal_cells.count()
        
        print(f"\nFound {count} rows in table")
        print("\nSignal order (should be: Extreme Oversold → Oversold → Neutral → Overbought → Extreme Overbought):")
        print("-" * 80)
        
        signals = []
        priority_map = {
            'Extreme Oversold': 5,
            'Oversold': 4,
            'Neutral': 3,
            'Overbought': 2,
            'Extreme Overbought': 1
        }
        
        for i in range(count):
            cell = signal_cells.nth(i)
            badge = cell.locator('.badge')
            if badge.count() > 0:
                signal_text = badge.inner_text().strip()
            else:
                signal_text = cell.inner_text().strip()
            signals.append(signal_text)
            priority = priority_map.get(signal_text, 0)
            print(f"Row {i+1:2d}: {signal_text:20s} (priority: {priority})")
        
        # Verify sorting
        print("\n" + "-" * 80)
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
            print("❌ Sorting errors found:")
            for error in errors:
                print(f"  - {error}")
            print("\n⚠️  Sorting is NOT working correctly!")
        else:
            print("✅ Sorting is working correctly!")
            print("   Order: Extreme Oversold → Oversold → Neutral → Overbought → Extreme Overbought")
        
        print("\nPress Enter to close the browser...")
        input()
        browser.close()


if __name__ == "__main__":
    print("=" * 80)
    print("Results Page Sorting Test")
    print("=" * 80)
    print("\nMake sure the server is running: python run.py")
    print("Then run this script to test sorting in a browser.\n")
    test_sorting()

