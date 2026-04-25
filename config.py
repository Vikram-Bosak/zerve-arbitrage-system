"""
Configuration for Zerve Arbitrage Detection System
"""

import os
from typing import List

class Config:
    """Application configuration"""
    
    # API Keys (Set these as environment variables)
    POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY", "")
    KALSHI_API_KEY = os.getenv("KALSHI_API_KEY", "")
    METACULUS_API_KEY = os.getenv("METACULUS_API_KEY", "")
    
    # API Endpoints
    POLYMARKET_API_URL = "https://api.polymarket.com"
    KALSHI_API_URL = "https://api.kalshi.com"
    METACULUS_API_URL = "https://api.metaculus.com"
    
    # Data Collection Settings
    DATA_COLLECTION_INTERVAL = 300  # 5 minutes
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 30
    
    # ML Model Settings
    MODEL_UPDATE_INTERVAL = 3600  # 1 hour
    MIN_TRAINING_SAMPLES = 100
    MODEL_ACCURACY_THRESHOLD = 0.85
    
    # Arbitrage Detection Settings
    MIN_ARBITRAGE_PERCENTAGE = 5.0  # 5% minimum arbitrage
    MAX_RISK_SCORE = 0.7  # Maximum acceptable risk
    CONFIDENCE_THRESHOLD = 0.8
    
    # Risk Analysis Settings
    RISK_FREE_RATE = 0.02  # 2% annual risk-free rate
    MAX_POSITION_SIZE = 10000  # Maximum position size
    DIVERSIFICATION_THRESHOLD = 0.3
    
    # API Settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_RELOAD = True
    
    # Dashboard Settings
    DASHBOARD_HOST = "0.0.0.0"
    DASHBOARD_PORT = 8501
    
    # Data Storage
    DATA_DIR = "data"
    MODELS_DIR = "models"
    OUTPUTS_DIR = "outputs"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "arbitrage_system.log"
    
    # Markets to Monitor
    MONITORED_MARKETS = [
        "polymarket",
        "kalshi", 
        "metaculus"
    ]
    
    # Categories to Analyze
    ANALYSIS_CATEGORIES = [
        "elections",
        "economics",
        "technology",
        "sports",
        "climate"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        required_keys = [
            "POLYMARKET_API_KEY",
            "KALSHI_API_KEY", 
            "METACULUS_API_KEY"
        ]
        
        for key in required_keys:
            if not getattr(cls, key):
                print(f"Warning: {key} not set. Set as environment variable.")
                return False
        
        return True

# Create directories
def create_directories():
    """Create necessary directories"""
    import os
    directories = [
        Config.DATA_DIR,
        Config.MODELS_DIR,
        Config.OUTPUTS_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    print("Configuration validated:", Config.validate())
    print("Directories created successfully")
