"""Configuration settings for Arthos application."""
import os
from typing import Optional

# FMP API Configuration
# The actual API key should be set as an environment variable: FMP_API_KEY
# This masked value is just a placeholder and should not be used
FMP_API_KEY: Optional[str] = os.getenv("FMP_API_KEY", "***MASKED***")

# FMP API Base URL (using stable version as per documentation)
FMP_API_BASE_URL = "https://financialmodelingprep.com/stable"

# Validate that API key is set (warn if using masked value)
if FMP_API_KEY == "***MASKED***":
    import warnings
    warnings.warn(
        "FMP_API_KEY environment variable not set. FMP API calls will fail. "
        "Set FMP_API_KEY environment variable with your API key.",
        UserWarning
    )

