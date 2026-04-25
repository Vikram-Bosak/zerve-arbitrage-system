"""
Streamlit Dashboard - Interactive web dashboard for arbitrage detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

from config import Config
from main import ArbitrageSystem
from utils import logger

# Page configuration
st.set_page_config(
    page_title="Arbitrage Detection Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = None
    st.session_state.last_analysis = None
    st.session_state.analysis_count = 0

def load_latest_results():
    """Load latest analysis results"""
    results_dir = "outputs"
    if not os.path.exists(results_dir):
        return None
    
    results_files = [f for f in os.listdir(results_dir) if f.startswith("analysis_results_")]
    if not results_files:
        return None
    
    latest_file = sorted(results_files)[-1]
    filepath = os.path.join(results_dir, latest_file)
    
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 AI-Powered Arbitrage Detection System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <p><strong>ZerveHack Submission</strong> | Real-time arbitrage detection across prediction markets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Controls")
    
    # Analysis controls
    st.sidebar.subheader("🔍 Analysis")
    run_analysis = st.sidebar.button("🚀 Run New Analysis", type="primary")
    min_arbitrage = st.sidebar.slider("Min Arbitrage %", 0.0, 50.0, 5.0, 0.5)
    max_risk = st.sidebar.slider("Max Risk Score", 0.0, 1.0, 0.7, 0.1)
    
    # Display controls
    st.sidebar.subheader("📊 Display")
    show_top_n = st.sidebar.slider("Show Top N", 5, 50, 10)
    show_risk_analysis = st.sidebar.checkbox("Show Risk Analysis", True)
    show_ml_insights = st.sidebar.checkbox("Show ML Insights", True)
    
    # Run analysis
    if run_analysis:
        with st.spinner("Running analysis... This may take a few minutes."):
            try:
                if st.session_state.system is None:
                    st.session_state.system = ArbitrageSystem()
                
                results = st.session_state.system.run_full_analysis()
                st.session_state.last_analysis = results
                st.session_state.analysis_count += 1
                
                st.success("✅ Analysis completed successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error running analysis: {str(e)}")
                logger.error(f"Dashboard analysis error: {e}")
    
    # Load latest results
    results = st.session_state.last_analysis or load_latest_results()
    
    if not results:
        st.warning("⚠️ No analysis results available. Click 'Run New Analysis' to get started.")
        st.info("💡 First time? The system will collect data from Polymarket, Kalshi, and Metaculus, then detect arbitrage opportunities.")
        return
    
    # Display metrics
    st.header("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Opportunities",
            f"{results['opportunities']['total_count']}",
            delta=f"Filtered: {results['opportunities']['filtered_count']}"
        )
    
    with col2:
        st.metric(
            "Average Arbitrage",
            f"{results['metrics']['avg_arbitrage']:.2f}%",
            delta=f"Max: {results['metrics']['max_arbitrage']:.2f}%"
        )
    
    with col3:
        st.metric(
            "Success Rate",
            f"{results['metrics']['success_rate']:.1f}%",
            delta="ML Prediction"
        )
    
    with col4:
        st.metric(
            "Sharpe Ratio",
            f"{results['metrics']['sharpe_ratio']:.2f}",
            delta="Risk-Adjusted"
        )
    
    # Top opportunities
    st.header("🏆 Top Arbitrage Opportunities")
    
    opportunities = results['opportunities']['top_opportunities']
    
    # Filter opportunities
    filtered_opps = [
        opp for opp in opportunities
        if opp['arbitrage'] >= min_arbitrage and opp['risk_score'] <= max_risk
    ]
    
    if not filtered_opps:
        st.warning("No opportunities match your filters. Try adjusting the criteria.")
    else:
        # Display opportunities table
        opps_df = pd.DataFrame(filtered_opps[:show_top_n])
        
        # Format columns
        display_cols = [
            'market', 'question', 'arbitrage', 'profit', 'roi',
            'risk_score', 'risk_level', 'success_probability'
        ]
        
        opps_df_display = opps_df[display_cols].copy()
        opps_df_display['arbitrage'] = opps_df_display['arbitrage'].apply(lambda x: f"{x:.2f}%")
        opps_df_display['profit'] = opps_df_display['profit'].apply(lambda x: f"${x:.2f}")
        opps_df_display['roi'] = opps_df_display['roi'].apply(lambda x: f"{x:.2f}%")
        opps_df_display['risk_score'] = opps_df_display['risk_score'].apply(lambda x: f"{x:.3f}")
        opps_df_display['success_probability'] = opps_df_display['success_probability'].apply(lambda x: f"{x*100:.1f}%")
        
        opps_df_display.columns = [
            'Market', 'Question', 'Arbitrage', 'Profit', 'ROI',
            'Risk Score', 'Risk Level', 'Success Prob'
        ]
        
        st.dataframe(
            opps_df_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Visualizations
        st.header("📊 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Arbitrage distribution
            fig_arbitrage = px.histogram(
                opps_df,
                x='arbitrage',
                nbins=20,
                title='Arbitrage Distribution',
                labels={'arbitrage': 'Arbitrage %'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_arbitrage.update_layout(
                xaxis_title="Arbitrage %",
                yaxis_title="Count",
                showlegend=False
            )
            st.plotly_chart(fig_arbitrage, use_container_width=True)
        
        with col2:
            # Risk vs Return
            fig_risk_return = px.scatter(
                opps_df,
                x='risk_score',
                y='arbitrage',
                size='profit',
                color='risk_level',
                title='Risk vs Return',
                labels={
                    'risk_score': 'Risk Score',
                    'arbitrage': 'Arbitrage %',
                    'profit': 'Profit ($)'
                },
                hover_data=['market', 'question']
            )
            fig_risk_return.update_layout(
                xaxis_title="Risk Score",
                yaxis_title="Arbitrage %"
            )
            st.plotly_chart(fig_risk_return, use_container_width=True)
        
        # Platform comparison
        st.header("🔄 Platform Comparison")
        
        platform_data = []
        for opp in filtered_opps:
            platform_data.append({
                'Platform': opp['platform1'],
                'Arbitrage': opp['arbitrage'],
                'Volume': opp['volume']
            })
            platform_data.append({
                'Platform': opp['platform2'],
                'Arbitrage': opp['arbitrage'],
                'Volume': opp['volume']
            })
        
        platform_df = pd.DataFrame(platform_data)
        
        if not platform_df.empty:
            fig_platform = px.box(
                platform_df,
                x='Platform',
                y='Arbitrage',
                title='Arbitrage by Platform',
                color='Platform'
            )
            fig_platform.update_layout(
                xaxis_title="Platform",
                yaxis_title="Arbitrage %"
            )
            st.plotly_chart(fig_platform, use_container_width=True)
    
    # Risk analysis
    if show_risk_analysis:
        st.header("⚠️ Risk Analysis")
        
        risk_analysis = results['risk_analysis']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Portfolio Risk",
                risk_analysis['portfolio_risk_level'],
                delta=f"Score: {risk_analysis['avg_risk']:.3f}"
            )
        
        with col2:
            st.metric(
                "Diversification",
                f"{risk_analysis['diversification_score']:.2f}",
                delta=f"{risk_analysis['platform_count']} platforms"
            )
        
        with col3:
            st.metric(
                "Risk Std Dev",
                f"{risk_analysis['risk_std']:.3f}",
                delta="Consistency"
            )
        
        # Risk distribution
        risk_dist = risk_analysis['risk_distribution']
        
        fig_risk_dist = go.Figure(data=[
            go.Bar(
                x=list(risk_dist.keys()),
                y=list(risk_dist.values()),
                marker_color=['#2ecc71', '#f39c12', '#e74c3c', '#8e44ad']
            )
        ])
        
        fig_risk_dist.update_layout(
            title='Risk Distribution',
            xaxis_title='Risk Level',
            yaxis_title='Count'
        )
        
        st.plotly_chart(fig_risk_dist, use_container_width=True)
    
    # ML insights
    if show_ml_insights:
        st.header("🤖 ML Model Insights")
        
        ml_results = results['ml_results']
        
        # Movement predictor results
        if ml_results['movement_predictor'].get('success'):
            st.subheader("Price Movement Predictor")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Test MSE",
                    f"{ml_results['movement_predictor']['test_mse']:.6f}",
                    delta="Lower is better"
                )
            
            with col2:
                st.metric(
                    "CV Score",
                    f"{ml_results['movement_predictor']['cv_mean']:.4f}",
                    delta=f"±{ml_results['movement_predictor']['cv_std']:.4f}"
                )
            
            # Feature importance
            feature_importance = ml_results['movement_predictor'].get('feature_importance', {})
            if feature_importance:
                st.write("**Top Features:**")
                feat_df = pd.DataFrame(
                    list(feature_importance.items()),
                    columns=['Feature', 'Importance']
                ).sort_values('Importance', ascending=False).head(10)
                
                fig_feat = px.bar(
                    feat_df,
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    title='Feature Importance'
                )
                st.plotly_chart(fig_feat, use_container_width=True)
        
        # Arbitrage classifier results
        if ml_results['arbitrage_classifier'].get('success'):
            st.subheader("Arbitrage Success Classifier")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Train Accuracy",
                    f"{ml_results['arbitrage_classifier']['train_accuracy']:.3f}",
                    delta="Training"
                )
            
            with col2:
                st.metric(
                    "Test Accuracy",
                    f"{ml_results['arbitrage_classifier']['test_accuracy']:.3f}",
                    delta="Testing"
                )
    
    # Recommendations
    st.header("💡 Recommendations")
    
    recommendations = results['recommendations']
    
    for i, rec in enumerate(recommendations, 1):
        if i == 1:
            st.markdown(f'<div class="success-box">{rec}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">{rec}</div>', unsafe_allow_html=True)
    
    # System info
    st.header("ℹ️ System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Analysis Time",
            f"{results['metadata']['analysis_duration']:.2f}s",
            delta="Performance"
        )
    
    with col2:
        st.metric(
            "Total Analyses",
            st.session_state.analysis_count,
            delta="Session"
        )
    
    with col3:
        st.metric(
            "Last Update",
            datetime.fromisoformat(results['metadata']['timestamp']).strftime("%H:%M:%S"),
            delta="Real-time"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏆 <strong>ZerveHack Submission</strong> | AI-Powered Arbitrage Detection System</p>
        <p>Built with ❤️ using FastAPI, Streamlit, scikit-learn, and Zerve Platform</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
