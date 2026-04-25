"""
Streamlit Dashboard - Simple standalone version for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎯 AI-Powered Arbitrage Detection System</h1>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Controls")

# Load demo data option
load_demo = st.sidebar.button("🔄 Load Demo Data")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Markets", "80")
with col2:
    st.metric("Platforms", "4")
with col3:
    st.metric("Categories", "8")

st.markdown("---")

# Generate demo data
if load_demo or 'demo_data' not in st.session_state:
    with st.spinner("Generating demo data..."):
        # Create sample arbitrage opportunities
        np.random.seed(42)
        
        demo_data = {
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
        
        df = pd.DataFrame(demo_data)
        st.session_state.demo_data = df
        st.success("✅ Demo data loaded!")

# Display data
if 'demo_data' in st.session_state:
    df = st.session_state.demo_data
    
    # Metrics
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Opportunities", len(df))
    with col2:
        st.metric("Avg Arbitrage", f"{df['arbitrage'].mean():.2f}%")
    with col3:
        st.metric("Max Arbitrage", f"{df['arbitrage'].max():.2f}%")
    with col4:
        st.metric("Total Profit", f"${df['profit'].sum():,.2f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Arbitrage by Market")
        fig = px.bar(df, x='market', y='arbitrage', 
                     color='risk_level',
                     title='Arbitrage Opportunities',
                     labels={'arbitrage': 'Arbitrage %', 'market': 'Market'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Profit Distribution")
        fig = px.pie(df, values='profit', names='market',
                     title='Profit Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed table
    st.subheader("📋 Detailed Opportunities")
    
    # Add color coding for risk levels
    def highlight_risk(val):
        if val == 'HIGH':
            return 'background-color: #ffcccc'
        elif val == 'MEDIUM':
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #d4edda'
    
    styled_df = df.style.applymap(highlight_risk, subset=['risk_level'])
    st.dataframe(styled_df, use_container_width=True)
    
    st.markdown("---")
    
    # Platform comparison
    st.subheader("🔄 Platform Comparison")
    
    platform_stats = df.groupby('platform1').agg({
        'arbitrage': 'mean',
        'profit': 'sum'
    }).reset_index()
    
    fig = px.scatter(platform_stats, x='platform1', y='arbitrage',
                     size='profit', color='platform1',
                     title='Platform Performance',
                     labels={'platform1': 'Platform', 'arbitrage': 'Avg Arbitrage %'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Risk analysis
    st.subheader("🛡️ Risk Analysis")
    
    risk_counts = df['risk_level'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                     title='Risk Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.info(f"""
        **Risk Summary:**
        - High Risk: {risk_counts.get('HIGH', 0)} opportunities
        - Medium Risk: {risk_counts.get('MEDIUM', 0)} opportunities
        - Low Risk: {risk_counts.get('LOW', 0)} opportunities
        """)
    
    st.markdown("---")
    
    # Download button
    st.subheader("📥 Export Data")
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"arbitrage_opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Click 'Load Demo Data' to see arbitrage opportunities!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏆 AI-Powered Arbitrage Detection System | ZerveHack Submission</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
