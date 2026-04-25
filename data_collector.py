"""
Data Collector Module - Collects data from prediction market APIs
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time
import json

from config import Config
from utils import logger, setup_logging

class DataCollector:
    """Collects data from multiple prediction market APIs"""
    
    def __init__(self):
        """Initialize data collector"""
        self.config = Config
        self.session = requests.Session()
        self.cache = {}
        self.cache_expiry = {}
        
        logger.info("DataCollector initialized")
    
    def _make_request(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request with retry logic
        
        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data or None
        """
        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Max retries exceeded for {url}")
                    return None
    
    def collect_polymarket_data(self) -> List[Dict]:
        """
        Collect data from Polymarket API
        
        Returns:
            List of market data
        """
        logger.info("Collecting Polymarket data...")
        
        # Simulated data (replace with actual API call)
        # In production, use: self._make_request(self.config.POLYMARKET_API_URL + "/markets")
        
        simulated_data = [
            {
                "market_id": "poly_001",
                "market": "US Election 2024",
                "question": "Will Biden win?",
                "yes_price": 0.52,
                "no_price": 0.48,
                "volume": 1500000,
                "liquidity": 500000,
                "timestamp": datetime.now().isoformat(),
                "platform": "polymarket"
            },
            {
                "market_id": "poly_002",
                "market": "Fed Rate Cut",
                "question": "Will Fed cut rates in June?",
                "yes_price": 0.35,
                "no_price": 0.65,
                "volume": 800000,
                "liquidity": 300000,
                "timestamp": datetime.now().isoformat(),
                "platform": "polymarket"
            },
            {
                "market_id": "poly_003",
                "market": "AI Breakthrough",
                "question": "Will AGI be achieved by 2027?",
                "yes_price": 0.25,
                "no_price": 0.75,
                "volume": 2000000,
                "liquidity": 800000,
                "timestamp": datetime.now().isoformat(),
                "platform": "polymarket"
            }
        ]
        
        logger.info(f"Collected {len(simulated_data)} Polymarket markets")
        return simulated_data
    
    def collect_kalshi_data(self) -> List[Dict]:
        """
        Collect data from Kalshi API
        
        Returns:
            List of market data
        """
        logger.info("Collecting Kalshi data...")
        
        # Simulated data (replace with actual API call)
        simulated_data = [
            {
                "market_id": "kalshi_001",
                "market": "Fed Rate Decision",
                "question": "Will Fed cut rates by 25bps?",
                "yes_price": 0.40,
                "no_price": 0.60,
                "volume": 1200000,
                "liquidity": 400000,
                "timestamp": datetime.now().isoformat(),
                "platform": "kalshi"
            },
            {
                "market_id": "kalshi_002",
                "market": "GDP Growth",
                "question": "Will Q2 GDP exceed 2%?",
                "yes_price": 0.55,
                "no_price": 0.45,
                "volume": 900000,
                "liquidity": 350000,
                "timestamp": datetime.now().isoformat(),
                "platform": "kalshi"
            },
            {
                "market_id": "kalshi_003",
                "market": "Inflation Rate",
                "question": "Will CPI stay below 3%?",
                "yes_price": 0.48,
                "no_price": 0.52,
                "volume": 700000,
                "liquidity": 250000,
                "timestamp": datetime.now().isoformat(),
                "platform": "kalshi"
            }
        ]
        
        logger.info(f"Collected {len(simulated_data)} Kalshi markets")
        return simulated_data
    
    def collect_metaculus_data(self) -> List[Dict]:
        """
        Collect data from Metaculus API
        
        Returns:
            List of market data
        """
        logger.info("Collecting Metaculus data...")
        
        # Simulated data (replace with actual API call)
        simulated_data = [
            {
                "market_id": "meta_001",
                "market": "AGI Timeline",
                "question": "AGI by 2027?",
                "community_prediction": 0.22,
                "metaculus_prediction": 0.20,
                "forecasters": 450,
                "timestamp": datetime.now().isoformat(),
                "platform": "metaculus"
            },
            {
                "market_id": "meta_002",
                "market": "Climate Goals",
                "question": "1.5°C target achieved?",
                "community_prediction": 0.15,
                "metaculus_prediction": 0.12,
                "forecasters": 380,
                "timestamp": datetime.now().isoformat(),
                "platform": "metaculus"
            },
            {
                "market_id": "meta_003",
                "market": "Space Exploration",
                "question": "Humans on Mars by 2030?",
                "community_prediction": 0.18,
                "metaculus_prediction": 0.15,
                "forecasters": 520,
                "timestamp": datetime.now().isoformat(),
                "platform": "metaculus"
            }
        ]
        
        logger.info(f"Collected {len(simulated_data)} Metaculus markets")
        return simulated_data
    
    def collect_all_data(self) -> Dict[str, List[Dict]]:
        """
        Collect data from all platforms
        
        Returns:
            Dictionary of platform data
        """
        logger.info("Starting data collection from all platforms...")
        
        all_data = {
            "polymarket": self.collect_polymarket_data(),
            "kalshi": self.collect_kalshi_data(),
            "metaculus": self.collect_metaculus_data()
        }
        
        total_markets = sum(len(data) for data in all_data.values())
        logger.info(f"Data collection complete. Total markets: {total_markets}")
        
        return all_data
    
    def normalize_market_data(self, raw_data: Dict[str, List[Dict]]) -> pd.DataFrame:
        """
        Normalize market data from different platforms
        
        Args:
            raw_data: Raw data from all platforms
            
        Returns:
            Normalized DataFrame
        """
        logger.info("Normalizing market data...")
        
        normalized_data = []
        
        for platform, markets in raw_data.items():
            for market in markets:
                # Normalize based on platform
                if platform == "polymarket":
                    normalized = {
                        "market_id": market["market_id"],
                        "market": market["market"],
                        "question": market["question"],
                        "yes_price": market["yes_price"],
                        "no_price": market["no_price"],
                        "volume": market["volume"],
                        "liquidity": market["liquidity"],
                        "timestamp": market["timestamp"],
                        "platform": platform
                    }
                elif platform == "kalshi":
                    normalized = {
                        "market_id": market["market_id"],
                        "market": market["market"],
                        "question": market["question"],
                        "yes_price": market["yes_price"],
                        "no_price": market["no_price"],
                        "volume": market["volume"],
                        "liquidity": market["liquidity"],
                        "timestamp": market["timestamp"],
                        "platform": platform
                    }
                elif platform == "metaculus":
                    # Convert Metaculus prediction to yes/no prices
                    pred = market["community_prediction"]
                    normalized = {
                        "market_id": market["market_id"],
                        "market": market["market"],
                        "question": market["question"],
                        "yes_price": pred,
                        "no_price": 1 - pred,
                        "volume": market["forecasters"] * 100,  # Estimate
                        "liquidity": market["forecasters"] * 50,
                        "timestamp": market["timestamp"],
                        "platform": platform
                    }
                
                normalized_data.append(normalized)
        
        df = pd.DataFrame(normalized_data)
        logger.info(f"Normalized {len(df)} market records")
        
        return df
    
    def save_data(self, data: pd.DataFrame, filename: str = "market_data.csv"):
        """
        Save collected data to file
        
        Args:
            data: DataFrame to save
            filename: Output filename
        """
        import os
        
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        filepath = f"{self.config.DATA_DIR}/{filename}"
        
        data.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")
    
    def load_data(self, filename: str = "market_data.csv") -> Optional[pd.DataFrame]:
        """
        Load data from file
        
        Args:
            filename: Input filename
            
        Returns:
            DataFrame or None
        """
        import os
        
        filepath = f"{self.config.DATA_DIR}/{filename}"
        
        if not os.path.exists(filepath):
            logger.warning(f"Data file not found: {filepath}")
            return None
        
        df = pd.read_csv(filepath)
        logger.info(f"Data loaded from {filepath}")
        
        return df

if __name__ == "__main__":
    # Test data collector
    setup_logging()
    
    collector = DataCollector()
    
    # Collect data
    raw_data = collector.collect_all_data()
    
    # Normalize data
    normalized_data = collector.normalize_market_data(raw_data)
    
    # Save data
    collector.save_data(normalized_data)
    
    # Display summary
    print("\n" + "="*80)
    print("DATA COLLECTION SUMMARY")
    print("="*80)
    print(f"Total Markets: {len(normalized_data)}")
    print(f"Platforms: {normalized_data['platform'].nunique()}")
    print(f"Categories: {normalized_data['market'].nunique()}")
    print("\nSample Data:")
    print(normalized_data.head())
    print("\nData collection test completed successfully!")
