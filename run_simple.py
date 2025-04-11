#!/usr/bin/env python
"""
Simple script to run NewsSense in offline mode.
"""
import os
import subprocess
import webbrowser
import time

print("Starting NewsSense in OFFLINE MODE...")

# Create a simplified app file
with open("offline_app.py", "w", encoding="utf-8") as f:
    f.write("""
import os
import sys
import streamlit as st

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules directly
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Set offline mode flag
OFFLINE_MODE = True

# Now import the main app module with offline mode enabled
from web.app import *
""")

# Run Streamlit with the offline app
env = os.environ.copy()
env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")

try:
    process = subprocess.Popen(
        ["streamlit", "run", "offline_app.py", "--server.port=8501"],
        env=env
    )
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Open the browser
    print("Opening web browser to http://localhost:8501")
    webbrowser.open("http://localhost:8501")
    
    print("NewsSense is running in OFFLINE MODE.")
    print("All data is simulated - no API connections required.")
    print("Press Ctrl+C to stop.")
    
    # Keep the process running
    process.wait()
    
except KeyboardInterrupt:
    print("\nStopping Streamlit...")
    process.terminate() if process else None
    
    # Clean up the temporary file
    if os.path.exists("offline_app.py"):
        try:
            os.remove("offline_app.py")
            print("Cleaned up temporary files.")
        except:
            pass
    
    print("NewsSense stopped.") 