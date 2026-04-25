"""
Demo Analysis Pipeline - Uses demo data to show arbitrage detection
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
from arbitrage_detector import ArbitrageDetector
from ml_models import MLPredictor
from risk_analyzer import RiskAnalyzer

class DemoArbitrageSystem:
    """Demo arbitrage detection system using generated data"""
    
    def __init__(self):
        """Initialize the system"""
        self.config = Config
        setup_logging(self.config.LOG_FILE)
        
        # Initialize components
        self.arbitrage_detector = ArbitrageDetector()
        self.ml_predictor = MLPredictor()
        self.risk_analyzer = RiskAnalyzer()
        
        logger.info("DemoArbitrageSystem initialized")
    
    def load_demo_data(self) -> pd.DataFrame:
        """Load demo market data"""
        logger.info("Loading demo market data...")
        
        if os.path.exists('data/demo_market_data.csv'):
            df = pd.read_csv('data/demo_market_data.csv')
            logger.info(f"Loaded {len(df)} markets from demo data")
            return df
        else:
            logger.error("Demo data file not found!")
            raise FileNotFoundError("Please run demo_data_generator.py first")
    
    def run_demo_analysis(self) -> Dict:
        """Run complete arbitrage analysis on demo data"""
        start_time = datetime.now()
        
        logger.info("="*80)
        logger.info("STARTING DEMO ARBITRAGE ANALYSIS")
        logger.info("="*80)
        
        # Step 1: Load demo data
        logger.info("\n[STEP 1/5] Loading Demo Data")
        market_data = self.load_demo_data()
        
        # Step 2: Arbitrage Detection
        logger.info("\n[STEP 2/5] Arbitrage Detection")
        logger.info("Scanning for arbitrage opportunities...")
        
        opportunities = self.arbitrage_detector.scan_all_opportunities(market_data)
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        
        # Step 3: ML Model Training & Prediction
        logger.info("\n[STEP 3/5] ML Model Training & Prediction")
        
        # Train movement predictor
        if len(market_data) >= self.config.MIN_TRAINING_SAMPLES:
            movement_results = self.ml_predictor.train_movement_predictor(market_data)
        else:
            movement_results = {'success': False, 'error': 'Insufficient data'}
        
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
                'version': '1.0.0',
                'data_source': 'demo_data'
            },
            'data_summary': {
                'total_markets': len(market_data),
                'platforms': market_data['platform'].nunique(),
                'categories': market_data['category'].nunique()
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
        save_results(final_results, f"demo_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Generate reports
        arbitrage_report = self.arbitrage_detector.generate_opportunities_report(risk_adjusted_opportunities)
        risk_report = self.risk_analyzer.generate_risk_report(risk_adjusted_opportunities)
        
        # Save reports
        with open(f"outputs/demo_arbitrage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(arbitrage_report)
        
        with open(f"outputs/demo_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(risk_report)
        
        logger.info("\n" + "="*80)
        logger.info("DEMO ANALYSIS COMPLETED SUCCESSFULLY")
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
        
        # Count by risk level
        risk_counts = {}
        for opp in opportunities:
            risk_level = opp.get('risk_level', 'UNKNOWN')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Generate recommendations based on risk distribution
        high_risk_count = risk_counts.get('HIGH', 0) + risk_counts.get('VERY HIGH', 0)
        low_risk_count = risk_counts.get('LOW', 0)
        
        if low_risk_count > 0:
            recommendations.append(f"✅ {low_risk_count} low-risk opportunities available for immediate action")
        
        if high_risk_count > 0:
            recommendations.append(f"⚠️  {high_risk_count} high-risk opportunities - proceed with caution")
        
        # Top opportunity recommendation
        if opportunities:
            top_opp = opportunities[0]
            recommendations.append(
                f"🎯 Best opportunity: {top_opp['market']} with {top_opp['arbitrage']:.2f}% arbitrage"
            )
        
        return recommendations
    
    def get_summary(self, results: Dict) -> str:
        """Generate a human-readable summary"""
        summary = f"""
{'='*80}
🎯 ARBITRAGE DETECTION SYSTEM - DEMO RESULTS
{'='*80}

📊 DATA SUMMARY
{'-'*80}
Total Markets Analyzed: {results['data_summary']['total_markets']}
Platforms Monitored: {results['data_summary']['platforms']}
Categories Covered: {results['data_summary']['categories']}

💰 OPPORTUNITIES FOUND
{'-'*80}
Total Opportunities: {results['opportunities']['total_count']}
Low Risk Opportunities: {results['opportunities']['filtered_count']}

📈 ARBITRAGE METRICS
{'-'*80}
Average Arbitrage: {results['metrics']['avg_arbitrage']:.2f}%
Max Arbitrage: {results['metrics']['max_arbitrage']:.2f}%
Total Potential Profit: ${results['metrics']['total_potential_profit']:,.2f}

⚡ PERFORMANCE METRICS
{'-'*80}
Success Rate: {results['metrics']['success_rate']:.1f}%
Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}
Max Drawdown: {results['metrics']['max_drawdown']:.2f}%
Volatility: {results['metrics']['volatility']:.2f}%

🛡️  RISK ANALYSIS
{'-'*80}
Portfolio Risk: {results['risk_analysis']['portfolio_risk_level']}
Avg Risk Score: {results['risk_analysis']['avg_risk']:.3f}
Diversification: {results['risk_analysis']['diversification_score']:.2f}

🏆 TOP 3 OPPORTUNITIES
{'-'*80}
"""
        for i, opp in enumerate(results['opportunities']['top_opportunities'][:3], 1):
            summary += f"\n{i}. {opp['market']}\n"
            summary += f"   Arbitrage: {opp['arbitrage']:.2f}% | ROI: {opp['roi']:.2f}%\n"
            summary += f"   Risk: {opp['risk_level']} | Success Prob: {opp.get('success_probability', 0)*100:.1f}%\n"
        
        summary += f"\n💡 RECOMMENDATIONS\n{'-'*80}\n"
        for rec in results['recommendations']:
            summary += f"• {rec}\n"
        
        summary += f"\n{'='*80}\n"
        
        return summary

def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🎯 AI-POWERED ARBITRAGE DETECTION SYSTEM - DEMO")
    print("ZerveHack Submission - First Prize Project")
    print("="*80 + "\n")
    
    # Initialize system
    system = DemoArbitrageSystem()
    
    # Run analysis
    results = system.run_demo_analysis()
    
    # Generate and display summary
    summary = system.get_summary(results)
    print(summary)
    
    # Save summary
    with open("outputs/demo_analysis_summary.txt", "w") as f:
        f.write(summary)
    
    print("\n✅ Demo analysis completed successfully!")
    print("📊 Results saved to outputs/ directory")
    print("🎯 Ready for ZerveHack submission!")

if __name__ == "__main__":
    main()
