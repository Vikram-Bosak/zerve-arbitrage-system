#!/usr/bin/env python3
"""
Quick verification script
"""

import sys

print("🧪 Quick Dashboard Verification")
print("="*40)

# Test 1: Check file exists
try:
    with open('dashboard.py', 'r') as f:
        content = f.read()
        print("✅ dashboard.py exists")
except:
    print("❌ dashboard.py not found")
    sys.exit(1)

# Test 2: Check imports
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    print("✅ All imports work")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 3: Check syntax
try:
    compile(content, 'dashboard.py', 'exec')
    print("✅ Dashboard syntax is valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)

print("="*40)
print("✅ Dashboard is ready!")
print("🚀 Deploy to Streamlit Cloud now!")
