"""
Arbitrage Detector Module - Detects arbitrage opportunities across markets
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

from config import Config
from utils import (
    logger, calculate_percentage_difference, calculate_arbitrage_profit,
    calculate_sharpe_ratio, calculate_max_drawdown, calculate_volatility
)

class ArbitrageDetector:
    """Detects arbitrage opportunities across prediction markets"""
    
    def __init__(self):
        """Initialize arbitrage detector"""
        self.config = Config
        self.opportunities = []
        
        logger.info("ArbitrageDetector initialized")
    
    def find_matching_markets(self, data: pd.DataFrame) -> List[Tuple[pd.Series, pd.Series]]:
        """
        Find markets that are similar across platforms
        
        Args:
            data: DataFrame with market data
            
        Returns:
            List of matching market pairs
        """
        logger.info("Finding matching markets across platforms...")
        
        matches = []
        
        # Group by market name similarity
        for market_name in data['market'].unique():
            market_data = data[data['market'] == market_name]
            
            # If market exists on multiple platforms
            if len(market_data) > 1:
                # Create all possible pairs
                for i in range(len(market_data)):
                    for j in range(i + 1, len(market_data)):
                        pair = (market_data.iloc[i], market_data.iloc[j])
                        matches.append(pair)
        
        logger.info(f"Found {len(matches)} matching market pairs")
        return matches
    
    def detect_arbitrage(
        self,
        market1: pd.Series,
        market2: pd.Series
    ) -> Optional[Dict]:
        """
        Detect arbitrage opportunity between two markets
        
        Args:
            market1: First market data
            market2: Second market data
            
        Returns:
            Arbitrage opportunity details or None
        """
        try:
            # Calculate price differences
            yes_diff = calculate_percentage_difference(
                market1['yes_price'],
                market2['yes_price']
            )
            
            no_diff = calculate_percentage_difference(
                market1['no_price'],
                market2['no_price']
            )
            
            # Check if arbitrage opportunity exists
            if yes_diff < self.config.MIN_ARBITRAGE_PERCENTAGE and \
               no_diff < self.config.MIN_ARBITRAGE_PERCENTAGE:
                return None
            
            # Calculate arbitrage profit
            yes_profit = calculate_arbitrage_profit(
                market1['yes_price'],
                market2['yes_price'],
                1000  # $1000 position
            )
            
            no_profit = calculate_arbitrage_profit(
                market1['no_price'],
                market2['no_price'],
                1000
            )
            
            # Determine best opportunity
            if yes_profit['profit_percentage'] > no_profit['profit_percentage']:
                best_profit = yes_profit
                trade_type = "YES"
                buy_platform = market1['platform'] if market1['yes_price'] < market2['yes_price'] else market2['platform']
                sell_platform = market2['platform'] if market1['yes_price'] < market2['yes_price'] else market1['platform']
            else:
                best_profit = no_profit
                trade_type = "NO"
                buy_platform = market1['platform'] if market1['no_price'] < market2['no_price'] else market2['platform']
                sell_platform = market2['platform'] if market1['no_price'] < market2['no_price'] else market1['platform']
            
            # Calculate liquidity
            total_liquidity = market1['liquidity'] + market2['liquidity']
            
            # Create opportunity record
            opportunity = {
                'market': market1['market'],
                'question': market1['question'],
                'platform1': market1['platform'],
                'platform2': market2['platform'],
                'buy_platform': buy_platform,
                'sell_platform': sell_platform,
                'trade_type': trade_type,
                'price1': market1['yes_price'] if trade_type == "YES" else market1['no_price'],
                'price2': market2['yes_price'] if trade_type == "YES" else market2['no_price'],
                'arbitrage': best_profit['profit_percentage'],
                'profit': best_profit['profit'],
                'roi': best_profit['roi'],
                'volume': market1['volume'] + market2['volume'],
                'liquidity': total_liquidity,
                'timestamp': datetime.now().isoformat(),
                'risk_score': 0.5  # Will be calculated by risk analyzer
            }
            
            return opportunity
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage: {e}")
            return None
    
    def scan_all_opportunities(self, data: pd.DataFrame) -> List[Dict]:
        """
        Scan all markets for arbitrage opportunities
        
        Args:
            data: DataFrame with market data
            
        Returns:
            List of arbitrage opportunities
        """
        logger.info("Scanning for arbitrage opportunities...")
        
        # Find matching markets
        matches = self.find_matching_markets(data)
        
        # Detect arbitrage for each match
        opportunities = []
        for market1, market2 in matches:
            opportunity = self.detect_arbitrage(market1, market2)
            if opportunity:
                opportunities.append(opportunity)
        
        # Sort by arbitrage percentage
        opportunities.sort(key=lambda x: x['arbitrage'], reverse=True)
        
        self.opportunities = opportunities
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        
        return opportunities
    
    def filter_opportunities(
        self,
        opportunities: List[Dict],
        min_arbitrage: Optional[float] = None,
        max_risk: Optional[float] = None,
        min_liquidity: Optional[float] = None
    ) -> List[Dict]:
        """
        Filter opportunities based on criteria
        
        Args:
            opportunities: List of opportunities
            min_arbitrage: Minimum arbitrage percentage
            max_risk: Maximum risk score
            min_liquidity: Minimum liquidity
            
        Returns:
            Filtered opportunities
        """
        filtered = opportunities.copy()
        
        if min_arbitrage is not None:
            min_arbitrage = min_arbitrage or self.config.MIN_ARBITRAGE_PERCENTAGE
            filtered = [op for op in filtered if op['arbitrage'] >= min_arbitrage]
        
        if max_risk is not None:
            max_risk = max_risk or self.config.MAX_RISK_SCORE
            filtered = [op for op in filtered if op.get('risk_score', 1) <= max_risk]
        
        if min_liquidity is not None:
            filtered = [op for op in filtered if op['liquidity'] >= min_liquidity]
        
        logger.info(f"Filtered {len(opportunities)} -> {len(filtered)} opportunities")
        return filtered
    
    def calculate_opportunity_metrics(self, opportunities: List[Dict]) -> Dict:
        """
        Calculate aggregate metrics for opportunities
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            Dictionary of metrics
        """
        if not opportunities:
            return {
                'total_opportunities': 0,
                'avg_arbitrage': 0,
                'max_arbitrage': 0,
                'total_potential_profit': 0,
                'best_opportunity': None
            }
        
        arbitrage_values = [op['arbitrage'] for op in opportunities]
        profit_values = [op['profit'] for op in opportunities]
        
        metrics = {
            'total_opportunities': len(opportunities),
            'avg_arbitrage': np.mean(arbitrage_values),
            'median_arbitrage': np.median(arbitrage_values),
            'max_arbitrage': np.max(arbitrage_values),
            'min_arbitrage': np.min(arbitrage_values),
            'std_arbitrage': np.std(arbitrage_values),
            'total_potential_profit': sum(profit_values),
            'avg_profit': np.mean(profit_values),
            'best_opportunity': opportunities[0] if opportunities else None
        }
        
        return metrics
    
    def generate_opportunities_report(self, opportunities: List[Dict]) -> str:
        """
        Generate human-readable opportunities report
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            Report text
        """
        if not opportunities:
            return "No arbitrage opportunities found."
        
        lines = [
            "=" * 80,
            "ARBITRAGE OPPORTUNITIES REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Opportunities: {len(opportunities)}",
            "",
            "TOP OPPORTUNITIES",
            "-" * 80
        ]
        
        for i, opp in enumerate(opportunities[:10], 1):  # Top 10
            lines.extend([
                f"\n{i}. {opp['market']}",
                f"   Question: {opp['question']}",
                f"   Platforms: {opp['platform1']} ↔ {opp['platform2']}",
                f"   Trade: {opp['trade_type']} | Buy: {opp['buy_platform']} | Sell: {opp['sell_platform']}",
                f"   Arbitrage: {opp['arbitrage']:.2f}%",
                f"   Profit: ${opp['profit']:.2f}",
                f"   ROI: {opp['roi']:.2f}%",
                f"   Liquidity: ${opp['liquidity']:,.0f}",
                f"   Risk Score: {opp.get('risk_score', 'N/A')}"
            ])
        
        # Add metrics
        metrics = self.calculate_opportunity_metrics(opportunities)
        lines.extend([
            "",
            "-" * 80,
            "SUMMARY METRICS",
            "-" * 80,
            f"Average Arbitrage: {metrics['avg_arbitrage']:.2f}%",
            f"Median Arbitrage: {metrics['median_arbitrage']:.2f}%",
            f"Max Arbitrage: {metrics['max_arbitrage']:.2f}%",
            f"Total Potential Profit: ${metrics['total_potential_profit']:,.2f}",
            f"Average Profit: ${metrics['avg_profit']:.2f}",
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)

if __name__ == "__main__":
    # Test arbitrage detector
    from data_collector import DataCollector
    
    # Collect data
    collector = DataCollector()
    raw_data = collector.collect_all_data()
    normalized_data = collector.normalize_market_data(raw_data)
    
    # Detect arbitrage
    detector = ArbitrageDetector()
    opportunities = detector.scan_all_opportunities(normalized_data)
    
    # Generate report
    report = detector.generate_opportunities_report(opportunities)
    print(report)
    
    print("\nArbitrage detector test completed successfully!")
