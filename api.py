"""
FastAPI Module - REST API for arbitrage detection system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime
import uvicorn

from config import Config
from main import ArbitrageSystem
from utils import logger

# Initialize FastAPI app
app = FastAPI(
    title="Arbitrage Detection API",
    description="AI-Powered Arbitrage Detection System for Prediction Markets",
    version="1.0.0"
)

# Global system instance
system = None

class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    force_refresh: bool = False
    min_arbitrage: Optional[float] = None
    max_risk: Optional[float] = None

class OpportunityResponse(BaseModel):
    """Response model for opportunity"""
    market: str
    question: str
    arbitrage: float
    profit: float
    roi: float
    risk_score: float
    risk_level: str
    success_probability: float
    recommended_action: str

class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    timestamp: str
    total_opportunities: int
    avg_arbitrage: float
    total_potential_profit: float
    success_rate: float
    sharpe_ratio: float
    top_opportunities: List[OpportunityResponse]

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global system
    logger.info("Starting Arbitrage Detection API...")
    system = ArbitrageSystem()
    logger.info("API ready to serve requests")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Arbitrage Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/health": "Health check",
            "/api/analyze": "Run full analysis",
            "/api/opportunities": "Get current opportunities",
            "/api/metrics": "Get system metrics",
            "/docs": "API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_ready": system is not None
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Run full arbitrage analysis
    
    Args:
        request: Analysis request parameters
        background_tasks: Background tasks
        
    Returns:
        Analysis results
    """
    if system is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Run analysis
        results = system.run_full_analysis()
        
        # Extract top opportunities
        top_opps = results['opportunities']['top_opportunities'][:10]
        
        # Format response
        opportunities = [
            OpportunityResponse(
                market=opp['market'],
                question=opp['question'],
                arbitrage=opp['arbitrage'],
                profit=opp['profit'],
                roi=opp['roi'],
                risk_score=opp['risk_score'],
                risk_level=opp['risk_level'],
                success_probability=opp.get('success_probability', 0),
                recommended_action=opp['recommended_action']
            )
            for opp in top_opps
        ]
        
        response = AnalysisResponse(
            timestamp=results['metadata']['timestamp'],
            total_opportunities=results['opportunities']['total_count'],
            avg_arbitrage=results['metrics']['avg_arbitrage'],
            total_potential_profit=results['metrics']['total_potential_profit'],
            success_rate=results['metrics']['success_rate'],
            sharpe_ratio=results['metrics']['sharpe_ratio'],
            top_opportunities=opportunities
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities")
async def get_opportunities(
    min_arbitrage: Optional[float] = None,
    max_risk: Optional[float] = None,
    limit: int = 20
):
    """
    Get current arbitrage opportunities
    
    Args:
        min_arbitrage: Minimum arbitrage percentage
        max_risk: Maximum risk score
        limit: Maximum number of results
        
    Returns:
        List of opportunities
    """
    if system is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Get latest results
        from utils import load_results
        import os
        
        # Find latest results file
        results_dir = "outputs"
        if not os.path.exists(results_dir):
            return {"opportunities": [], "message": "No analysis results available"}
        
        results_files = [f for f in os.listdir(results_dir) if f.startswith("analysis_results_")]
        if not results_files:
            return {"opportunities": [], "message": "No analysis results available"}
        
        latest_file = sorted(results_files)[-1]
        results = load_results(latest_file.replace("analysis_results_", "").replace(".json", ""))
        
        if not results:
            return {"opportunities": [], "message": "No analysis results available"}
        
        # Filter opportunities
        opportunities = results['opportunities']['all_opportunities']
        
        if min_arbitrage:
            opportunities = [o for o in opportunities if o['arbitrage'] >= min_arbitrage]
        
        if max_risk:
            opportunities = [o for o in opportunities if o['risk_score'] <= max_risk]
        
        # Limit results
        opportunities = opportunities[:limit]
        
        return {
            "opportunities": opportunities,
            "total_count": len(opportunities),
            "timestamp": results['metadata']['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """
    Get system metrics
    
    Returns:
        System metrics
    """
    if system is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Get latest results
        from utils import load_results
        import os
        
        results_dir = "outputs"
        if not os.path.exists(results_dir):
            return {"message": "No metrics available"}
        
        results_files = [f for f in os.listdir(results_dir) if f.startswith("analysis_results_")]
        if not results_files:
            return {"message": "No metrics available"}
        
        latest_file = sorted(results_files)[-1]
        results = load_results(latest_file.replace("analysis_results_", "").replace(".json", ""))
        
        if not results:
            return {"message": "No metrics available"}
        
        return {
            "data_summary": results['data_summary'],
            "metrics": results['metrics'],
            "risk_analysis": results['risk_analysis'],
            "timestamp": results['metadata']['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary")
async def get_summary():
    """
    Get analysis summary
    
    Returns:
        Analysis summary
    """
    if system is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Get latest results
        from utils import load_results
        import os
        
        results_dir = "outputs"
        if not os.path.exists(results_dir):
            return {"summary": "No analysis results available"}
        
        results_files = [f for f in os.listdir(results_dir) if f.startswith("analysis_results_")]
        if not results_files:
            return {"summary": "No analysis results available"}
        
        latest_file = sorted(results_files)[-1]
        results = load_results(latest_file.replace("analysis_results_", "").replace(".json", ""))
        
        if not results:
            return {"summary": "No analysis results available"}
        
        # Generate summary
        summary = system.get_summary(results)
        
        return {
            "summary": summary,
            "timestamp": results['metadata']['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run API server
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD
    )
