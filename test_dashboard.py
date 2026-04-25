#!/usr/bin/env python3
"""
Test script to verify dashboard works
"""

import sys
import subprocess

def test_imports():
    """Test if all required imports work"""
    print("Testing imports...")
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dashboard_file():
    """Test if dashboard.py exists and is valid"""
    print("\nTesting dashboard.py...")
    try:
        with open('dashboard.py', 'r') as f:
            content = f.read()
            if 'streamlit' in content and 'st.' in content:
                print("✅ dashboard.py is valid!")
                return True
            else:
                print("❌ dashboard.py is invalid!")
                return False
    except FileNotFoundError:
        print("❌ dashboard.py not found!")
        return False

def test_streamlit_run():
    """Test if streamlit can run"""
    print("\nTesting Streamlit run...")
    try:
        result = subprocess.run(
            ['streamlit', 'run', 'dashboard.py', '--server.headless', 'true'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'You can now view your Streamlit app' in result.stdout or result.returncode == 0:
            print("✅ Streamlit can run dashboard!")
            return True
        else:
            print("❌ Streamlit failed to run!")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("🧪 Testing Streamlit Dashboard")
    print("="*50)
    
    results = []
    results.append(test_imports())
    results.append(test_dashboard_file())
    results.append(test_streamlit_run())
    
    print("\n" + "="*50)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("Dashboard is ready for deployment!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")
    print("="*50)
    
    sys.exit(0 if all(results) else 1)
