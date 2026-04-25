"""
Main Analysis Pipeline - Orchestrates the complete arbitrage detection system
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json
import os

from config import Config
from utils import (
    logger, setup_logging, save_results, generate_report,
    calculate_sharpe_ratio, calculate_max_drawdown, calculate_volatility
)
from data_collector import DataCollector
from arbitrage_detector import ArbitrageDetector
from ml_models import MLPredictor
from risk_analyzer import RiskAnalyzer

class ArbitrageSystem:
    """Main arbitrage detection system"""
    
    def __init__(self):
        """Initialize the system"""
        self.config = Config
        setup_logging(self.config.LOG_FILE)
        
        # Initialize components
        self.data_collector = DataCollector()
        self.arbitrage_detector = ArbitrageDetector()
        self.ml_predictor = MLPredictor()
        self.risk_analyzer = RiskAnalyzer()
        
        logger.info("ArbitrageSystem initialized")
    
    def run_full_analysis(self) -> Dict:
        """
        Run complete analysis pipeline
        
        Returns:
            Complete analysis results
        """
        logger.info("="*80)
        logger.info("STARTING FULL ARBITRAGE ANALYSIS")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        # Step 1: Data Collection
        logger.info("\n[STEP 1/5] Data Collection")
        raw_data = self.data_collector.collect_all_data()
        normalized_data = self.data_collector.normalize_market_data(raw_data)
        
        # Save data
        self.data_collector.save_data(normalized_data)
        
        # Step 2: Arbitrage Detection
        logger.info("\n[STEP 2/5] Arbitrage Detection")
        opportunities = self.arbitrage_detector.scan_all_opportunities(normalized_data)
        
        # Step 3: ML Predictions
        logger.info("\n[STEP 3/5] ML Model Training & Prediction")
        
        # Train movement predictor
        movement_results = self.ml_predictor.train_movement_predictor(normalized_data)
        
        # Train arbitrage classifier if enough opportunities
        if len(opportunities) >= self.config.MIN_TRAINING_SAMPLES:
            classifier_results = self.ml_predictor.train_arbitrage_classifier(opportunities)
        else:
            classifier_results = {'success': False, 'error': 'Insufficient opportunities'}
        
        # Predict success probabilities
        if len(opportunities) > 0:
            success_probs = self.ml_predictor.predict_arbitrage_success(opportunities)
            for i, opp in enumerate(opportunities):
                opp['success_probability'] = success_probs[i]
        
        # Save models
        self.ml_predictor.save_models()
        
        # Step 4: Risk Analysis
        logger.info("\n[STEP 4/5] Risk Analysis")
        risk_adjusted_opportunities = self.risk_analyzer.calculate_risk_adjusted_returns(opportunities)
        portfolio_risk = self.risk_analyzer.analyze_portfolio_risk(risk_adjusted_opportunities)
        
        # Step 5: Generate Results
        logger.info("\n[STEP 5/5] Generating Results")
        
        # Calculate metrics
        metrics = self.arbitrage_detector.calculate_opportunity_metrics(risk_adjusted_opportunities)
        
        # Calculate additional metrics
        if len(risk_adjusted_opportunities) > 0:
            returns = [opp['roi'] for opp in risk_adjusted_opportunities]
            sharpe = calculate_sharpe_ratio(returns)
            max_dd = calculate_max_drawdown(returns)
            vol = calculate_volatility(returns)
        else:
            sharpe = 0
            max_dd = 0
            vol = 0
        
        # Compile final results
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds()
        
        final_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'analysis_duration': analysis_duration,
                'version': '1.0.0'
            },
            'data_summary': {
                'total_markets': len(normalized_data),
                'platforms': normalized_data['platform'].nunique(),
                'categories': normalized_data['market'].nunique()
            },
            'opportunities': {
                'total_count': len(risk_adjusted_opportunities),
                'filtered_count': len([o for o in risk_adjusted_opportunities 
                                     if o['risk_score'] <= self.config.MAX_RISK_SCORE]),
                'top_opportunities': risk_adjusted_opportunities[:10],
                'all_opportunities': risk_adjusted_opportunities
            },
            'metrics': {
                'avg_arbitrage': metrics['avg_arbitrage'],
                'max_arbitrage': metrics['max_arbitrage'],
                'total_potential_profit': metrics['total_potential_profit'],
                'success_rate': np.mean([o.get('success_probability', 0) for o in risk_adjusted_opportunities]) * 100,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'volatility': vol
            },
            'risk_analysis': portfolio_risk,
            'ml_results': {
                'movement_predictor': movement_results,
                'arbitrage_classifier': classifier_results
            },
            'recommendations': self._generate_recommendations(risk_adjusted_opportunities)
        }
        
        # Save results
        save_results(final_results, f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Generate reports
        arbitrage_report = self.arbitrage_detector.generate_opportunities_report(risk_adjusted_opportunities)
        risk_report = self.risk_analyzer.generate_risk_report(risk_adjusted_opportunities)
        
        # Save reports
        with open(f"outputs/arbitrage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(arbitrage_report)
        
        with open(f"outputs/risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(risk_report)
        
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Duration: {analysis_duration:.2f} seconds")
        logger.info(f"Opportunities Found: {len(risk_adjusted_opportunities)}")
        logger.info(f"Average Arbitrage: {metrics['avg_arbitrage']:.2f}%")
        logger.info(f"Total Potential Profit: ${metrics['total_potential_profit']:,.2f}")
        
        return final_results
    
    def _generate_recommendations(self, opportunities: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not opportunities:
            recommendations.append("No arbitrage opportunities found at this time.")
            return recommendations
        
        # Top recommendation
        top_opp = opportunities[0]
        if top_opp['risk_score'] <= self.config.MAX_RISK_SCORE:
            recommendations.append(
                f"HIGH PRIORITY: {top_opp['market']} - {top_opp['arbitrage']:.2f}% arbitrage "
                f"with {top_opp['risk_level']} risk"
            )
        
        # Risk-based recommendations
        low_risk_count = len([o for o in opportunities if o['risk_score'] < 0.3])
        if low_risk_count > 0:
            recommendations.append(
                f"Consider {low_risk_count} low-risk opportunities for stable returns"
            )
        
        # Diversification recommendation
        platforms = set()
        for opp in opportunities:
            platforms.add(opp['platform1'])
            platforms.add(opp['platform2'])
        
        if len(platforms) > 2:
            recommendations.append(
                f"Good diversification across {len(platforms)} platforms"
            )
        
        # ML-based recommendation
        high_prob_count = len([o for o in opportunities if o.get('success_probability', 0) > 0.8])
        if high_prob_count > 0:
            recommendations.append(
                f"{high_prob_count} opportunities have >80% success probability"
            )
        
        return recommendations
    
    def get_summary(self, results: Dict) -> str:
        """Get human-readable summary"""
        lines = [
            "=" * 80,
            "ARBITRAGE DETECTION SYSTEM - ANALYSIS SUMMARY",
            "=" * 80,
            f"Generated: {results['metadata']['timestamp']}",
            f"Duration: {results['metadata']['analysis_duration']:.2f} seconds",
            "",
            "DATA SUMMARY",
            "-" * 80,
            f"Total Markets Analyzed: {results['data_summary']['total_markets']}",
            f"Platforms: {results['data_summary']['platforms']}",
            f"Categories: {results['data_summary']['categories']}",
            "",
            "OPPORTUNITIES",
            "-" * 80,
            f"Total Found: {results['opportunities']['total_count']}",
            f"Low Risk: {results['opportunities']['filtered_count']}",
            f"Average Arbitrage: {results['metrics']['avg_arbitrage']:.2f}%",
            f"Max Arbitrage: {results['metrics']['max_arbitrage']:.2f}%",
            f"Total Potential Profit: ${results['metrics']['total_potential_profit']:,.2f}",
            "",
            "PERFORMANCE METRICS",
            "-" * 80,
            f"Success Rate: {results['metrics']['success_rate']:.2f}%",
            f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}",
            f"Max Drawdown: {results['metrics']['max_drawdown']:.2f}%",
            f"Volatility: {results['metrics']['volatility']:.2f}%",
            "",
            "RISK ANALYSIS",
            "-" * 80,
            f"Portfolio Risk: {results['risk_analysis']['portfolio_risk_level']}",
            f"Avg Risk Score: {results['risk_analysis']['avg_risk']:.3f}",
            f"Diversification: {results['risk_analysis']['diversification_score']:.2f}",
            "",
            "TOP 3 OPPORTUNITIES",
            "-" * 80
        ]
        
        for i, opp in enumerate(results['opportunities']['top_opportunities'][:3], 1):
            lines.extend([
                f"\n{i}. {opp['market']}",
                f"   Arbitrage: {opp['arbitrage']:.2f}%",
                f"   Risk: {opp['risk_score']:.3f} ({opp['risk_level']})",
                f"   Profit: ${opp['profit']:.2f}",
                f"   Success Prob: {opp.get('success_probability', 0)*100:.1f}%"
            ])
        
        lines.extend([
            "",
            "RECOMMENDATIONS",
            "-" * 80
        ])
        
        for rec in results['recommendations']:
            lines.append(f"• {rec}")
        
        lines.extend([
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)

def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("AI-POWERED ARBITRAGE DETECTION SYSTEM")
    print("ZerveHack Submission - First Prize Project")
    print("="*80 + "\n")
    
    # Create system
    system = ArbitrageSystem()
    
    # Run analysis
    results = system.run_full_analysis()
    
    # Display summary
    summary = system.get_summary(results)
    print(summary)
    
    # Save summary
    with open("outputs/analysis_summary.txt", 'w') as f:
        f.write(summary)
    
    print("\n✅ Analysis completed successfully!")
    print("📊 Results saved to outputs/ directory")
    print("🎯 Ready for ZerveHack submission!")
    
    return results

if __name__ == "__main__":
    main()
