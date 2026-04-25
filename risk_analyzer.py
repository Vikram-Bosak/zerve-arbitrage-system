"""
Risk Analyzer Module - Analyzes risk for arbitrage opportunities
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

from config import Config
from utils import (
    logger, calculate_sharpe_ratio, calculate_max_drawdown,
    calculate_volatility, calculate_confidence_interval
)

class RiskAnalyzer:
    """Analyzes risk for arbitrage opportunities"""
    
    def __init__(self):
        """Initialize risk analyzer"""
        self.config = Config
        self.risk_factors = {}
        
        logger.info("RiskAnalyzer initialized")
    
    def calculate_liquidity_risk(self, opportunity: Dict) -> float:
        """
        Calculate liquidity risk score
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Risk score (0-1, higher is riskier)
        """
        liquidity = opportunity.get('liquidity', 0)
        volume = opportunity.get('volume', 0)
        
        # Lower liquidity = higher risk
        if liquidity < 100000:
            return 0.9
        elif liquidity < 500000:
            return 0.6
        elif liquidity < 1000000:
            return 0.3
        else:
            return 0.1
    
    def calculate_volatility_risk(self, opportunity: Dict) -> float:
        """
        Calculate volatility risk score
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Risk score (0-1, higher is riskier)
        """
        price_spread = abs(opportunity.get('price1', 0) - opportunity.get('price2', 0))
        
        # Higher spread = higher risk
        if price_spread > 0.3:
            return 0.8
        elif price_spread > 0.2:
            return 0.5
        elif price_spread > 0.1:
            return 0.3
        else:
            return 0.1
    
    def calculate_platform_risk(self, opportunity: Dict) -> float:
        """
        Calculate platform risk score
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Risk score (0-1, higher is riskier)
        """
        platform1 = opportunity.get('platform1', '')
        platform2 = opportunity.get('platform2', '')
        
        # Different platforms = higher risk (execution risk)
        if platform1 != platform2:
            return 0.4
        else:
            return 0.1
    
    def calculate_time_risk(self, opportunity: Dict) -> float:
        """
        Calculate time-based risk score
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Risk score (0-1, higher is riskier)
        """
        # For now, assume moderate time risk
        # In production, this would consider market closing times, etc.
        return 0.3
    
    def calculate_market_risk(self, opportunity: Dict) -> float:
        """
        Calculate market-specific risk score
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Risk score (0-1, higher is riskier)
        """
        market = opportunity.get('market', '').lower()
        
        # Different markets have different risk profiles
        if 'election' in market:
            return 0.5  # Political risk
        elif 'fed' in market or 'rate' in market:
            return 0.4  # Economic risk
        elif 'ai' in market or 'tech' in market:
            return 0.6  # Technology risk
        elif 'sport' in market:
            return 0.3  # Sports risk
        else:
            return 0.4  # Default risk
    
    def calculate_comprehensive_risk(
        self,
        opportunity: Dict,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Calculate comprehensive risk score
        
        Args:
            opportunity: Arbitrage opportunity
            weights: Risk factor weights
            
        Returns:
            Dictionary with risk scores
        """
        if weights is None:
            weights = {
                'liquidity': 0.3,
                'volatility': 0.25,
                'platform': 0.2,
                'time': 0.1,
                'market': 0.15
            }
        
        # Calculate individual risk factors
        liquidity_risk = self.calculate_liquidity_risk(opportunity)
        volatility_risk = self.calculate_volatility_risk(opportunity)
        platform_risk = self.calculate_platform_risk(opportunity)
        time_risk = self.calculate_time_risk(opportunity)
        market_risk = self.calculate_market_risk(opportunity)
        
        # Calculate weighted risk score
        total_risk = (
            weights['liquidity'] * liquidity_risk +
            weights['volatility'] * volatility_risk +
            weights['platform'] * platform_risk +
            weights['time'] * time_risk +
            weights['market'] * market_risk
        )
        
        risk_analysis = {
            'total_risk_score': total_risk,
            'liquidity_risk': liquidity_risk,
            'volatility_risk': volatility_risk,
            'platform_risk': platform_risk,
            'time_risk': time_risk,
            'market_risk': market_risk,
            'risk_level': self._get_risk_level(total_risk),
            'recommended_action': self._get_recommended_action(total_risk)
        }
        
        return risk_analysis
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level description"""
        if risk_score < 0.3:
            return "LOW"
        elif risk_score < 0.5:
            return "MEDIUM"
        elif risk_score < 0.7:
            return "HIGH"
        else:
            return "VERY HIGH"
    
    def _get_recommended_action(self, risk_score: float) -> str:
        """Get recommended action based on risk"""
        if risk_score < 0.3:
            return "PROCEED - Low risk opportunity"
        elif risk_score < 0.5:
            return "CAUTION - Monitor closely"
        elif risk_score < 0.7:
            return "HIGH RISK - Consider position sizing"
        else:
            return "AVOID - Too risky"
    
    def analyze_portfolio_risk(
        self,
        opportunities: List[Dict]
    ) -> Dict:
        """
        Analyze portfolio-level risk
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            Portfolio risk analysis
        """
        if not opportunities:
            return {
                'total_opportunities': 0,
                'avg_risk': 0,
                'risk_distribution': {},
                'diversification_score': 0,
                'portfolio_risk_level': 'LOW'
            }
        
        # Calculate individual risks
        risk_scores = []
        risk_levels = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'VERY HIGH': 0}
        
        for opp in opportunities:
            risk_analysis = self.calculate_comprehensive_risk(opp)
            risk_score = risk_analysis['total_risk_score']
            risk_scores.append(risk_score)
            risk_levels[risk_analysis['risk_level']] += 1
        
        # Calculate portfolio metrics
        avg_risk = np.mean(risk_scores)
        max_risk = np.max(risk_scores)
        min_risk = np.min(risk_scores)
        
        # Calculate diversification
        platforms = set()
        for opp in opportunities:
            platforms.add(opp.get('platform1', ''))
            platforms.add(opp.get('platform2', ''))
        
        diversification_score = len(platforms) / len(self.config.MONITORED_MARKETS)
        
        portfolio_analysis = {
            'total_opportunities': len(opportunities),
            'avg_risk': avg_risk,
            'max_risk': max_risk,
            'min_risk': min_risk,
            'risk_std': np.std(risk_scores),
            'risk_distribution': risk_levels,
            'diversification_score': diversification_score,
            'platform_count': len(platforms),
            'portfolio_risk_level': self._get_risk_level(avg_risk)
        }
        
        return portfolio_analysis
    
    def calculate_risk_adjusted_returns(
        self,
        opportunities: List[Dict]
    ) -> List[Dict]:
        """
        Calculate risk-adjusted returns for opportunities
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            Opportunities with risk-adjusted metrics
        """
        enhanced_opportunities = []
        
        for opp in opportunities:
            # Calculate risk
            risk_analysis = self.calculate_comprehensive_risk(opp)
            risk_score = risk_analysis['total_risk_score']
            
            # Calculate risk-adjusted return
            raw_return = opp.get('roi', 0)
            risk_adjusted_return = raw_return / (1 + risk_score * 10)  # Penalize high risk
            
            # Calculate Sharpe-like ratio
            sharpe_ratio = raw_return / (risk_score + 0.01)  # Avoid division by zero
            
            # Enhance opportunity
            enhanced_opp = opp.copy()
            enhanced_opp['risk_score'] = risk_score
            enhanced_opp['risk_level'] = risk_analysis['risk_level']
            enhanced_opp['risk_adjusted_return'] = risk_adjusted_return
            enhanced_opp['sharpe_ratio'] = sharpe_ratio
            enhanced_opp['recommended_action'] = risk_analysis['recommended_action']
            
            enhanced_opportunities.append(enhanced_opp)
        
        # Sort by risk-adjusted return
        enhanced_opportunities.sort(
            key=lambda x: x['risk_adjusted_return'],
            reverse=True
        )
        
        return enhanced_opportunities
    
    def generate_risk_report(self, opportunities: List[Dict]) -> str:
        """
        Generate risk analysis report
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            Report text
        """
        if not opportunities:
            return "No opportunities to analyze."
        
        # Calculate risk-adjusted returns
        enhanced_opps = self.calculate_risk_adjusted_returns(opportunities)
        
        # Portfolio analysis
        portfolio_risk = self.analyze_portfolio_risk(enhanced_opps)
        
        lines = [
            "=" * 80,
            "RISK ANALYSIS REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "PORTFOLIO RISK SUMMARY",
            "-" * 80,
            f"Total Opportunities: {portfolio_risk['total_opportunities']}",
            f"Average Risk Score: {portfolio_risk['avg_risk']:.3f}",
            f"Risk Range: {portfolio_risk['min_risk']:.3f} - {portfolio_risk['max_risk']:.3f}",
            f"Risk Std Dev: {portfolio_risk['risk_std']:.3f}",
            f"Diversification Score: {portfolio_risk['diversification_score']:.2f}",
            f"Platform Count: {portfolio_risk['platform_count']}",
            f"Portfolio Risk Level: {portfolio_risk['portfolio_risk_level']}",
            "",
            "RISK DISTRIBUTION",
            "-" * 80,
        ]
        
        for level, count in portfolio_risk['risk_distribution'].items():
            percentage = (count / portfolio_risk['total_opportunities']) * 100
            lines.append(f"{level}: {count} ({percentage:.1f}%)")
        
        lines.extend([
            "",
            "TOP OPPORTUNITIES (Risk-Adjusted)",
            "-" * 80
        ])
        
        for i, opp in enumerate(enhanced_opps[:10], 1):
            lines.extend([
                f"\n{i}. {opp['market']}",
                f"   Arbitrage: {opp['arbitrage']:.2f}%",
                f"   Risk Score: {opp['risk_score']:.3f} ({opp['risk_level']})",
                f"   Risk-Adjusted Return: {opp['risk_adjusted_return']:.2f}%",
                f"   Sharpe Ratio: {opp['sharpe_ratio']:.2f}",
                f"   Action: {opp['recommended_action']}"
            ])
        
        lines.extend([
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)

if __name__ == "__main__":
    # Test risk analyzer
    from data_collector import DataCollector
    from arbitrage_detector import ArbitrageDetector
    
    # Collect data
    collector = DataCollector()
    raw_data = collector.collect_all_data()
    normalized_data = collector.normalize_market_data(raw_data)
    
    # Detect arbitrage
    detector = ArbitrageDetector()
    opportunities = detector.scan_all_opportunities(normalized_data)
    
    # Analyze risk
    risk_analyzer = RiskAnalyzer()
    
    # Generate risk report
    report = risk_analyzer.generate_risk_report(opportunities)
    print(report)
    
    print("\nRisk analyzer test completed successfully!")
