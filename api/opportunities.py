"""
Vercel Serverless Function - Arbitrage API
"""

from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate demo data
        np.random.seed(42)
        
        data = {
            'market': [
                'Politics Arbitrage Event 10',
                'Sports Arbitrage Event 4',
                'Politics Arbitrage Event 2',
                'Finance Arbitrage Event 5',
                'Technology Arbitrage Event 7'
            ],
            'arbitrage': [75.91, 66.91, 103.49, 58.23, 72.15],
            'roi': [27.03, 24.57, 24.62, 21.89, 26.45],
            'risk_level': ['HIGH', 'HIGH', 'HIGH', 'MEDIUM', 'HIGH'],
            'platform1': ['Polymarket', 'Kalshi', 'Polymarket', 'Metaculus', 'Manifold'],
            'platform2': ['Kalshi', 'Polymarket', 'Metaculus', 'Polymarket', 'Kalshi'],
            'profit': [270.30, 245.70, 246.20, 218.90, 264.50]
        }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'success',
            'data': data,
            'metrics': {
                'total_opportunities': len(data['market']),
                'avg_arbitrage': np.mean(data['arbitrage']),
                'max_arbitrage': max(data['arbitrage']),
                'total_profit': sum(data['profit'])
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
