"""Run the Arthos FastAPI application."""
import uvicorn
import os
import getpass

def get_fmp_api_key():
    """
    Prompt user for FMP API key if not already set in environment.
    
    Returns:
        str: FMP API key
    """
    # Check if API key is already set
    existing_key = os.getenv("FMP_API_KEY")
    
    if existing_key and existing_key != "***MASKED***":
        print(f"✓ FMP_API_KEY already set in environment (length: {len(existing_key)})")
        return existing_key
    
    # Prompt for API key
    print("\n" + "="*60)
    print("FMP API Key Required")
    print("="*60)
    print("The application requires an FMP API key to fetch stock data.")
    print("You can:")
    print("  1. Enter the API key now (will be set for this session)")
    print("  2. Press Enter to skip (API calls will fail)")
    print("  3. Set FMP_API_KEY environment variable before running")
    print("="*60 + "\n")
    
    api_key = getpass.getpass("Enter FMP API key (input hidden): ").strip()
    
    if not api_key:
        print("\n⚠ Warning: No API key provided. FMP API calls will fail.")
        print("   Set FMP_API_KEY environment variable or provide it when prompted.\n")
        return None
    
    # Set as environment variable for this process
    os.environ["FMP_API_KEY"] = api_key
    print(f"✓ FMP API key set (length: {len(api_key)})\n")
    return api_key


if __name__ == "__main__":
    # Get FMP API key before starting server
    get_fmp_api_key()
    
    # Start the application
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

