"""
Utility functions for Zerve Arbitrage Detection System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logging(log_file: str = "arbitrage_system.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def calculate_percentage_difference(price1: float, price2: float) -> float:
    """Calculate percentage difference between two prices"""
    if price1 == 0 or price2 == 0:
        return 0.0
    return abs((price1 - price2) / ((price1 + price2) / 2)) * 100

def calculate_arbitrage_profit(
    price1: float, 
    price2: float, 
    position_size: float = 1000
) -> Dict[str, float]:
    """
    Calculate arbitrage profit
    
    Args:
        price1: Price on platform 1
        price2: Price on platform 2
        position_size: Size of position
        
    Returns:
        Dictionary with profit metrics
    """
    if price1 == 0 or price2 == 0:
        return {
            "profit": 0.0,
            "profit_percentage": 0.0,
            "roi": 0.0
        }
    
    # Buy at lower price, sell at higher price
    buy_price = min(price1, price2)
    sell_price = max(price1, price2)
    
    # Calculate profit
    profit = (sell_price - buy_price) * position_size
    profit_percentage = ((sell_price - buy_price) / buy_price) * 100
    roi = (profit / position_size) * 100
    
    return {
        "profit": profit,
        "profit_percentage": profit_percentage,
        "roi": roi
    }

def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate / 252  # Daily
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe * np.sqrt(252)  # Annualized

def calculate_max_drawdown(returns: List[float]) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        returns: List of returns
        
    Returns:
        Maximum drawdown percentage
    """
    if not returns:
        return 0.0
    
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    
    return abs(np.min(drawdown)) * 100

def calculate_volatility(returns: List[float]) -> float:
    """
    Calculate volatility (standard deviation)
    
    Args:
        returns: List of returns
        
    Returns:
        Annualized volatility
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    return np.std(returns) * np.sqrt(252) * 100

def calculate_confidence_interval(
    values: List[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate confidence interval
    
    Args:
        values: List of values
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if not values:
        return (0.0, 0.0)
    
    values_array = np.array(values)
    mean = np.mean(values_array)
    std_error = np.std(values_array) / np.sqrt(len(values_array))
    
    from scipy import stats
    z_score = stats.norm.ppf((1 + confidence) / 2)
    
    margin = z_score * std_error
    
    return (mean - margin, mean + margin)

def normalize_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize data using min-max scaling
    
    Args:
        data: DataFrame to normalize
        
    Returns:
        Normalized DataFrame
    """
    from sklearn.preprocessing import MinMaxScaler
    
    scaler = MinMaxScaler()
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    
    data_normalized = data.copy()
    data_normalized[numeric_columns] = scaler.fit_transform(data[numeric_columns])
    
    return data_normalized

def detect_outliers(
    data: pd.Series,
    method: str = "iqr",
    threshold: float = 1.5
) -> pd.Series:
    """
    Detect outliers in data
    
    Args:
        data: Series of values
        method: Detection method ('iqr' or 'zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean series indicating outliers
    """
    if method == "iqr":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == "zscore":
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > threshold
    
    return pd.Series([False] * len(data), index=data.index)

def calculate_correlation_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix
    
    Args:
        data: DataFrame with numeric columns
        
    Returns:
        Correlation matrix
    """
    return data.corr()

def format_currency(value: float, currency: str = "USD") -> str:
    """Format value as currency"""
    return f"{currency} {value:,.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"

def get_time_ranges() -> Dict[str, Tuple[datetime, datetime]]:
    """
    Get common time ranges for analysis
    
    Returns:
        Dictionary of time range names and (start, end) tuples
    """
    now = datetime.now()
    
    return {
        "last_hour": (now - timedelta(hours=1), now),
        "last_24h": (now - timedelta(hours=24), now),
        "last_week": (now - timedelta(days=7), now),
        "last_month": (now - timedelta(days=30), now),
        "last_quarter": (now - timedelta(days=90), now),
        "last_year": (now - timedelta(days=365), now)
    }

def save_results(results: Dict, filename: str):
    """
    Save results to file
    
    Args:
        results: Results dictionary
        filename: Output filename
    """
    import json
    import os
    
    os.makedirs("outputs", exist_ok=True)
    
    with open(f"outputs/{filename}", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to outputs/{filename}")

def load_results(filename: str) -> Optional[Dict]:
    """
    Load results from file
    
    Args:
        filename: Input filename
        
    Returns:
        Results dictionary or None
    """
    import json
    import os
    
    filepath = f"outputs/{filename}"
    
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_report(
    analysis_results: Dict,
    output_file: str = "arbitrage_report.txt"
) -> str:
    """
    Generate analysis report
    
    Args:
        analysis_results: Analysis results dictionary
        output_file: Output filename
        
    Returns:
        Report text
    """
    report_lines = [
        "=" * 80,
        "ARBITRAGE DETECTION SYSTEM - ANALYSIS REPORT",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SUMMARY",
        "-" * 80,
        f"Total Markets Analyzed: {analysis_results.get('total_markets', 0)}",
        f"Arbitrage Opportunities Found: {analysis_results.get('opportunities_count', 0)}",
        f"Average Arbitrage: {analysis_results.get('avg_arbitrage', 0):.2f}%",
        f"Success Rate: {analysis_results.get('success_rate', 0):.2f}%",
        "",
        "TOP OPPORTUNITIES",
        "-" * 80,
    ]
    
    for i, opp in enumerate(analysis_results.get('top_opportunities', []), 1):
        report_lines.append(
            f"{i}. {opp.get('market', 'N/A')} - "
            f"Arbitrage: {opp.get('arbitrage', 0):.2f}%, "
            f"Risk: {opp.get('risk', 0):.2f}"
        )
    
    report_lines.extend([
        "",
        "RISK ANALYSIS",
        "-" * 80,
        f"Average Risk Score: {analysis_results.get('avg_risk', 0):.2f}",
        f"Sharpe Ratio: {analysis_results.get('sharpe_ratio', 0):.2f}",
        f"Max Drawdown: {analysis_results.get('max_drawdown', 0):.2f}%",
        "",
        "=" * 80,
        "END OF REPORT",
        "=" * 80
    ])
    
    report_text = "\n".join(report_lines)
    
    # Save report
    with open(f"outputs/{output_file}", 'w') as f:
        f.write(report_text)
    
    logger.info(f"Report saved to outputs/{output_file}")
    
    return report_text

if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test arbitrage calculation
    profit = calculate_arbitrage_profit(0.45, 0.55, 1000)
    print(f"Arbitrage Profit: {profit}")
    
    # Test Sharpe ratio
    returns = [0.01, 0.02, -0.01, 0.03, 0.01]
    sharpe = calculate_sharpe_ratio(returns)
    print(f"Sharpe Ratio: {sharpe:.2f}")
    
    print("Utility functions tested successfully!")
