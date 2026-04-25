"""
Demo Data Generator - Creates realistic market data with arbitrage opportunities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def generate_demo_data(num_markets=50, num_opportunities=10):
    """
    Generate realistic demo data with arbitrage opportunities
    
    Args:
        num_markets: Total number of markets to generate
        num_opportunities: Number of arbitrage opportunities to create
    """
    print("🎯 Generating Demo Data with Arbitrage Opportunities...")
    
    # Define platforms
    platforms = ['Polymarket', 'Kalshi', 'Metaculus', 'Manifold']
    
    # Define market categories
    categories = [
        'Politics', 'Sports', 'Finance', 'Technology', 
        'Entertainment', 'Science', 'Climate', 'Health'
    ]
    
    # Generate base markets
    markets = []
    market_id = 0
    
    for i in range(num_markets):
        platform = np.random.choice(platforms)
        category = np.random.choice(categories)
        
        # Generate realistic prices
        yes_price = np.random.uniform(0.1, 0.9)
        no_price = 1 - yes_price
        
        # Add some noise
        yes_price += np.random.normal(0, 0.02)
        yes_price = np.clip(yes_price, 0.01, 0.99)
        no_price = 1 - yes_price
        
        # Generate volume
        volume = np.random.randint(1000, 1000000)
        
        # Generate liquidity score
        liquidity = np.random.uniform(0.5, 1.0)
        
        market = {
            'market_id': f"market_{market_id}",
            'platform': platform,
            'market': f"{category} Event {i+1}",
            'question': f"Will {category} Event {i+1} occur?",
            'category': category,
            'yes_price': round(yes_price, 4),
            'no_price': round(no_price, 4),
            'volume': volume,
            'liquidity': round(liquidity, 4),
            'timestamp': (datetime.now() - timedelta(hours=np.random.randint(0, 24))).isoformat()
        }
        
        markets.append(market)
        market_id += 1
    
    # Create arbitrage opportunities by creating matching markets with price differences
    print(f"📊 Creating {num_opportunities} arbitrage opportunities...")
    
    for i in range(num_opportunities):
        # Pick a random category
        category = np.random.choice(categories)
        
        # Create two markets with price difference
        base_price = np.random.uniform(0.3, 0.7)
        
        # Platform 1 - lower price
        market1 = {
            'market_id': f"arbitrage_{i}_1",
            'platform': platforms[0],
            'market': f"{category} Arbitrage Event {i+1}",
            'question': f"Will {category} Arbitrage Event {i+1} occur?",
            'category': category,
            'yes_price': round(base_price - np.random.uniform(0.05, 0.15), 4),
            'no_price': round(1 - (base_price - np.random.uniform(0.05, 0.15)), 4),
            'volume': np.random.randint(50000, 500000),
            'liquidity': round(np.random.uniform(0.7, 1.0), 4),
            'timestamp': datetime.now().isoformat()
        }
        
        # Platform 2 - higher price
        market2 = {
            'market_id': f"arbitrage_{i}_2",
            'platform': platforms[1],
            'market': f"{category} Arbitrage Event {i+1}",
            'question': f"Will {category} Arbitrage Event {i+1} occur?",
            'category': category,
            'yes_price': round(base_price + np.random.uniform(0.05, 0.15), 4),
            'no_price': round(1 - (base_price + np.random.uniform(0.05, 0.15)), 4),
            'volume': np.random.randint(50000, 500000),
            'liquidity': round(np.random.uniform(0.7, 1.0), 4),
            'timestamp': datetime.now().isoformat()
        }
        
        markets.extend([market1, market2])
    
    # Convert to DataFrame
    df = pd.DataFrame(markets)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/demo_market_data.csv', index=False)
    
    print(f"✅ Generated {len(df)} markets")
    print(f"📈 Total arbitrage opportunities: {num_opportunities}")
    print(f"💾 Data saved to data/demo_market_data.csv")
    
    return df

if __name__ == "__main__":
    # Generate demo data
    demo_df = generate_demo_data(num_markets=50, num_opportunities=15)
    
    # Display sample
    print("\n📊 Sample Data:")
    print(demo_df.head(10).to_string())
    
    # Display statistics
    print("\n📈 Statistics:")
    print(f"Total Markets: {len(demo_df)}")
    print(f"Platforms: {demo_df['platform'].nunique()}")
    print(f"Categories: {demo_df['category'].nunique()}")
    print(f"Average Yes Price: {demo_df['yes_price'].mean():.4f}")
    print(f"Average Volume: ${demo_df['volume'].mean():,.0f}")
